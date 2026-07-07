"""Менеджер кампаний обзвона."""

import asyncio
import csv
import logging
from datetime import datetime, time
from pathlib import Path

from pydantic import BaseModel, Field

from .call_session import CallSession
from .knowledge_base import get_knowledge_base
from .lead_storage import Lead, get_lead_storage
from .mango_client import MangoClient

logger = logging.getLogger(__name__)


class Contact(BaseModel):
    """Контакт из базы."""
    phone: str
    name: str | None = None
    company: str | None = None
    region: str | None = None
    description: str | None = None
    email: str | None = None
    website: str | None = None
    address: str | None = None


class Campaign(BaseModel):
    """Кампания обзвона."""
    name: str
    csv_path: Path
    status: str = "active"  # active, paused, completed
    max_retries: int = 3
    retry_delays: list[int] = Field(default=[15, 60, 180])  # минут
    call_hours_start: int = 9
    call_hours_end: int = 18
    max_concurrent: int = 5

    # Статистика
    total_contacts: int = 0
    called_count: int = 0
    success_count: int = 0
    interested_count: int = 0


class CampaignManager:
    """Менеджер кампаний обзвона."""

    def __init__(
        self,
        mango_client: MangoClient,
        llm_api_key: str = ""
    ):
        self.mango_client = mango_client
        self.llm_api_key = llm_api_key
        self.active_campaigns: dict[str, Campaign] = {}
        self.active_sessions: dict[str, CallSession] = {}
        self._call_queue: asyncio.Queue = asyncio.Queue()
        self._is_running = False

    def load_campaign(self, name: str, csv_path: Path) -> Campaign:
        """
        Загрузка кампании из CSV.

        Args:
            name: Название кампании
            csv_path: Путь к CSV файлу

        Returns:
            Объект кампании
        """
        # Подсчет контактов
        contacts = self._load_contacts(csv_path)

        campaign = Campaign(
            name=name,
            csv_path=csv_path,
            total_contacts=len(contacts)
        )

        self.active_campaigns[name] = campaign

        logger.info(f"Campaign loaded: {name}, contacts: {len(contacts)}")
        return campaign

    def _load_contacts(self, csv_path: Path) -> list[Contact]:
        """Загрузка контактов из CSV."""
        contacts = []

        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # Извлекаем телефон
                    phone = row.get("Телефоны", row.get("phone", ""))
                    if not phone:
                        continue

                    # Очищаем телефон
                    phone = self._clean_phone(phone)
                    if not phone:
                        continue

                    contact = Contact(
                        phone=phone,
                        name=row.get("Имя", row.get("name")),
                        company=row.get("Название", row.get("company")),
                        region=row.get("Регион", row.get("region")),
                        description=row.get("Описание", row.get("description")),
                        email=row.get("Email", row.get("email")),
                        website=row.get("Сайт", row.get("website")),
                        address=row.get("Адрес", row.get("address"))
                    )

                    contacts.append(contact)

            logger.info(f"Loaded {len(contacts)} contacts from {csv_path}")

        except Exception as e:
            logger.error(f"Failed to load contacts: {e}")

        return contacts

    def _clean_phone(self, phone: str) -> str:
        """Очистка и нормализация телефона."""
        # Удаляем все кроме цифр и +
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")

        # Если начинается на 8, заменяем на 7
        if cleaned.startswith("8") and len(cleaned) == 11:
            cleaned = "7" + cleaned[1:]

        # Если нет +, добавляем
        if not cleaned.startswith("+"):
            cleaned = "+" + cleaned

        # Проверяем длину
        if len(cleaned) < 10 or len(cleaned) > 15:
            return ""

        return cleaned

    async def start_campaign(self, campaign_name: str):
        """Запуск кампании."""
        if campaign_name not in self.active_campaigns:
            logger.error(f"Campaign not found: {campaign_name}")
            return

        campaign = self.active_campaigns[campaign_name]
        campaign.status = "active"

        # Загружаем контакты
        contacts = self._load_contacts(campaign.csv_path)

        # Проверяем время звонков
        if not self._is_call_hours(campaign):
            logger.info("Not call hours, waiting...")
            return

        # Добавляем в очередь
        for contact in contacts:
            await self._call_queue.put((campaign_name, contact))

        # Запускаем обзвон
        self._is_running = True
        asyncio.create_task(self._process_queue())

        logger.info(f"Campaign started: {campaign_name}")

    async def _process_queue(self):
        """Обработка очереди звонков."""
        while self._is_running and not self._call_queue.empty():
            try:
                campaign_name, contact = await asyncio.wait_for(
                    self._call_queue.get(),
                    timeout=1.0
                )

                # Проверяем лимит параллельных звонков
                if len(self.active_sessions) >= 5:
                    await asyncio.sleep(1)
                    continue

                # Инициируем звонок
                await self._initiate_call(campaign_name, contact)

            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue processing error: {e}")

    async def _initiate_call(self, campaign_name: str, contact: Contact):
        """Инициация звонка."""
        campaign = self.active_campaigns.get(campaign_name)
        if not campaign:
            return

        try:
            # Проверяем, не звонили ли уже
            lead_storage = get_lead_storage()
            existing_lead = lead_storage.get_lead(contact.phone)
            if existing_lead and existing_lead.status in ["completed", "interested"]:
                logger.debug(f"Already called: {contact.phone}")
                return

            # Инициируем callback через Mango
            result = await self.mango_client.initiate_callback(
                number=contact.phone,
                extension="1"
            )

            if result.get("result") == 0:
                call_id = result.get("call_id", "")

                # Создаем сессию
                session = CallSession(
                    call_id=call_id,
                    phone=contact.phone,
                    mango_client=self.mango_client,
                    knowledge_base=get_knowledge_base(),
                    llm_api_key=self.llm_api_key
                )

                self.active_sessions[call_id] = session

                # Создаем запись лида
                lead = Lead(
                    phone=contact.phone,
                    call_id=call_id,
                    status="initiated"
                )
                lead_storage.save_lead(lead)

                # Обновляем статистику кампании
                campaign.called_count += 1

                logger.info(f"Call initiated: {contact.phone} -> {call_id}")

        except Exception as e:
            logger.error(f"Failed to initiate call to {contact.phone}: {e}")

    async def handle_call_answered(self, call_id: str):
        """Обработка ответа на звонок."""
        session = self.active_sessions.get(call_id)
        if session:
            await session.start()
            logger.info(f"Call answered: {call_id}")

    async def handle_call_audio(self, call_id: str, audio_data: bytes):
        """Обработка аудио от клиента."""
        session = self.active_sessions.get(call_id)
        if session:
            response = await session.process_client_audio(audio_data)
            logger.debug(f"Agent response: {response[:50]}...")

    async def handle_call_ended(self, call_id: str, reason: str = "completed"):
        """Обработка завершения звонка."""
        session = self.active_sessions.get(call_id)
        if session:
            await session.end(reason)

            # Обновляем лид
            lead_storage = get_lead_storage()
            lead_storage.update_lead_from_session(call_id, session.lead_info)

            # Удаляем сессию
            del self.active_sessions[call_id]

            logger.info(f"Call ended: {call_id}, reason: {reason}")

    def pause_campaign(self, campaign_name: str):
        """Пауза кампании."""
        if campaign_name in self.active_campaigns:
            self.active_campaigns[campaign_name].status = "paused"
            logger.info(f"Campaign paused: {campaign_name}")

    def resume_campaign(self, campaign_name: str):
        """Возобновление кампании."""
        if campaign_name in self.active_campaigns:
            self.active_campaigns[campaign_name].status = "active"
            logger.info(f"Campaign resumed: {campaign_name}")

    def stop_campaign(self, campaign_name: str):
        """Остановка кампании."""
        if campaign_name in self.active_campaigns:
            self.active_campaigns[campaign_name].status = "completed"
            logger.info(f"Campaign stopped: {campaign_name}")

    def _is_call_hours(self, campaign: Campaign) -> bool:
        """Проверка времени звонков."""
        now = datetime.now().time()
        return time(campaign.call_hours_start, 0) <= now <= time(campaign.call_hours_end, 0)

    def get_campaign_stats(self, campaign_name: str) -> dict:
        """Получение статистики кампании."""
        campaign = self.active_campaigns.get(campaign_name)
        if not campaign:
            return {}

        return {
            "name": campaign.name,
            "status": campaign.status,
            "total_contacts": campaign.total_contacts,
            "called_count": campaign.called_count,
            "success_count": campaign.success_count,
            "interested_count": campaign.interested_count,
            "active_sessions": len(self.active_sessions)
        }

    def get_all_stats(self) -> dict:
        """Получение общей статистики."""
        return {
            "campaigns": {
                name: self.get_campaign_stats(name)
                for name in self.active_campaigns
            },
            "active_sessions": len(self.active_sessions),
            "queue_size": self._call_queue.qsize()
        }


# Глобальный экземпляр
_campaign_manager: CampaignManager | None = None


def get_campaign_manager() -> CampaignManager:
    """Получить глобальный экземпляр менеджера кампаний."""
    global _campaign_manager
    if _campaign_manager is None:
        from .config import settings
        from .mango_client import MangoClient

        mango_client = MangoClient(
            api_key=settings.mango.api_key,
            salt=settings.mango.salt
        )

        _campaign_manager = CampaignManager(
            mango_client=mango_client,
            llm_api_key=settings.openrouter.api_key
        )
    return _campaign_manager
