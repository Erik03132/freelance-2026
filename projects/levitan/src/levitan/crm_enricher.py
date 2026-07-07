"""CRM enrichment — поиск контактных данных по номеру телефона."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from levitan.utils import normalize_phone

logger = logging.getLogger(__name__)


@dataclass
class ContactInfo:
    name: str = ""
    company: str = ""
    position: str = ""
    email: str = ""
    phone: str = ""
    source: str = ""

    @property
    def is_empty(self) -> bool:
        return not any([self.name, self.company, self.position, self.email])


class CrmProvider(ABC):
    @abstractmethod
    async def lookup(self, phone: str) -> ContactInfo: ...


class MockCrmProvider(CrmProvider):
    async def lookup(self, phone: str) -> ContactInfo:
        normalized = normalize_phone(phone)
        if normalized.endswith("6393030"):
            return ContactInfo(
                name="Иван Петров",
                company="ООО Технологии",
                position="Директор",
                phone=normalized,
                source="mock",
            )
        return ContactInfo(phone=normalized)


class CrmEnricher:
    def __init__(self, provider: CrmProvider | None = None):
        self._provider = provider or MockCrmProvider()

    async def enrich(self, phone: str) -> ContactInfo:
        contact = await self._provider.lookup(phone)
        if not contact.is_empty:
            logger.info("CRM enrichment found: %s (%s)", contact.name, contact.company)
        else:
            logger.info("CRM enrichment: no data for %s", phone)
        return contact
