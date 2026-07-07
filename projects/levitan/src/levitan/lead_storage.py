"""Хранение лидов в SQLite."""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Lead(BaseModel):
    """Модель лида."""
    phone: str
    call_id: str
    duration_sec: int = 0
    status: str = "initiated"  # initiated, active, completed, failed
    
    # Квалификация
    has_interest: bool = False
    crops: list[str] = []
    volume: Optional[str] = None
    region: Optional[str] = None
    basis: Optional[str] = None
    harvest_time: Optional[str] = None
    
    # Контакты
    contact_name: Optional[str] = None
    best_time_to_call: Optional[str] = None
    preferred_channel: Optional[str] = None
    email: Optional[str] = None
    
    # Возражения и заметки
    objections: list[str] = []
    notes: str = ""
    
    # Техническое
    confidence: float = 0.0
    transcript_path: Optional[str] = None
    audio_url: Optional[str] = None
    
    # Временные метки
    created_at: str = ""
    updated_at: str = ""


class LeadStorage:
    """Хранение лидов в SQLite."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    call_id TEXT UNIQUE,
                    duration_sec INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'initiated',
                    
                    has_interest BOOLEAN DEFAULT FALSE,
                    crops TEXT DEFAULT '[]',
                    volume TEXT,
                    region TEXT,
                    basis TEXT,
                    harvest_time TEXT,
                    
                    contact_name TEXT,
                    best_time_to_call TEXT,
                    preferred_channel TEXT,
                    email TEXT,
                    
                    objections TEXT DEFAULT '[]',
                    notes TEXT DEFAULT '',
                    
                    confidence REAL DEFAULT 0.0,
                    transcript_path TEXT,
                    audio_url TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_lead(self, lead: Lead) -> int:
        """
        Сохранение лида.
        
        Args:
            lead: Объект лида
            
        Returns:
            ID лида
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO leads (
                    phone, call_id, duration_sec, status,
                    has_interest, crops, volume, region, basis, harvest_time,
                    contact_name, best_time_to_call, preferred_channel, email,
                    objections, notes, confidence, transcript_path, audio_url,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.phone,
                lead.call_id,
                lead.duration_sec,
                lead.status,
                lead.has_interest,
                str(lead.crops),
                lead.volume,
                lead.region,
                lead.basis,
                lead.harvest_time,
                lead.contact_name,
                lead.best_time_to_call,
                lead.preferred_channel,
                lead.email,
                str(lead.objections),
                lead.notes,
                lead.confidence,
                lead.transcript_path,
                lead.audio_url,
                lead.created_at or datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            lead_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Lead saved: {lead_id} ({lead.phone})")
            return lead_id
            
        except Exception as e:
            logger.error(f"Failed to save lead: {e}")
            return -1
    
    def get_lead(self, phone: str) -> Optional[Lead]:
        """
        Получение лида по телефону.
        
        Args:
            phone: Телефон
            
        Returns:
            Объект лида или None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM leads WHERE phone = ?", (phone,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_lead(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get lead: {e}")
            return None
    
    def get_lead_by_call_id(self, call_id: str) -> Optional[Lead]:
        """Получение лида по call_id."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM leads WHERE call_id = ?", (call_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_lead(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get lead by call_id: {e}")
            return None
    
    def get_leads(
        self,
        status: Optional[str] = None,
        has_interest: Optional[bool] = None,
        region: Optional[str] = None,
        limit: int = 100
    ) -> list[Lead]:
        """
        Получение списка лидов.
        
        Args:
            status: Фильтр по статусу
            has_interest: Фильтр по заинтересованности
            region: Фильтр по региону
            limit: Лимит результатов
            
        Returns:
            Список лидов
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM leads WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if has_interest is not None:
                query += " AND has_interest = ?"
                params.append(has_interest)
            
            if region:
                query += " AND region = ?"
                params.append(region)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_lead(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get leads: {e}")
            return []
    
    def update_lead_status(self, call_id: str, status: str):
        """Обновление статуса лида."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE leads 
                SET status = ?, updated_at = ?
                WHERE call_id = ?
            """, (status, datetime.now().isoformat(), call_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Lead status updated: {call_id} -> {status}")
            
        except Exception as e:
            logger.error(f"Failed to update lead status: {e}")
    
    def update_lead_from_session(self, call_id: str, lead_info: dict):
        """Обновление лида из данных сессии."""
        try:
            lead = self.get_lead_by_call_id(call_id)
            if lead:
                # Обновляем поля
                if "has_interest" in lead_info:
                    lead.has_interest = lead_info["has_interest"]
                if "crops" in lead_info:
                    lead.crops = lead_info["crops"]
                if "volume" in lead_info:
                    lead.volume = lead_info["volume"]
                if "region" in lead_info:
                    lead.region = lead_info["region"]
                if "basis" in lead_info:
                    lead.basis = lead_info["basis"]
                if "harvest_time" in lead_info:
                    lead.harvest_time = lead_info["harvest_time"]
                if "contact_name" in lead_info:
                    lead.contact_name = lead_info["contact_name"]
                if "objections" in lead_info:
                    lead.objections = lead_info["objections"]
                if "notes" in lead_info:
                    lead.notes = lead_info["notes"]
                if "status" in lead_info:
                    lead.status = lead_info["status"]
                
                self.save_lead(lead)
                
                logger.info(f"Lead updated from session: {call_id}")
            
        except Exception as e:
            logger.error(f"Failed to update lead from session: {e}")
    
    def get_statistics(self) -> dict:
        """Получение статистики по лидам."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Всего лидов
            cursor.execute("SELECT COUNT(*) FROM leads")
            stats["total"] = cursor.fetchone()[0]
            
            # По статусам
            cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
            stats["by_status"] = dict(cursor.fetchall())
            
            # Заинтересованные
            cursor.execute("SELECT COUNT(*) FROM leads WHERE has_interest = 1")
            stats["interested"] = cursor.fetchone()[0]
            
            # По регионам
            cursor.execute("SELECT region, COUNT(*) FROM leads WHERE region IS NOT NULL GROUP BY region")
            stats["by_region"] = dict(cursor.fetchall())
            
            # По культурам
            cursor.execute("SELECT crops FROM leads WHERE crops != '[]'")
            crops_rows = cursor.fetchall()
            crops_count = {}
            for row in crops_rows:
                import ast
                crops = ast.literal_eval(row[0])
                for crop in crops:
                    crops_count[crop] = crops_count.get(crop, 0) + 1
            stats["by_crop"] = crops_count
            
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def _row_to_lead(self, row) -> Lead:
        """Конвертация строки БД в объект Lead."""
        import ast
        
        return Lead(
            phone=row[1],
            call_id=row[2],
            duration_sec=row[3],
            status=row[4],
            has_interest=bool(row[5]),
            crops=ast.literal_eval(row[6]) if row[6] else [],
            volume=row[7],
            region=row[8],
            basis=row[9],
            harvest_time=row[10],
            contact_name=row[11],
            best_time_to_call=row[12],
            preferred_channel=row[13],
            email=row[14],
            objections=ast.literal_eval(row[15]) if row[15] else [],
            notes=row[16] or "",
            confidence=row[17] or 0.0,
            transcript_path=row[18],
            audio_url=row[19],
            created_at=row[20] or "",
            updated_at=row[21] or ""
        )
    
    def export_to_csv(self, output_path: Path):
        """Экспорт лидов в CSV."""
        import csv
        
        leads = self.get_leads(limit=10000)
        
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # Заголовки
                writer.writerow([
                    "phone", "status", "has_interest", "crops", "volume",
                    "region", "basis", "harvest_time", "contact_name",
                    "notes", "created_at"
                ])
                
                # Данные
                for lead in leads:
                    writer.writerow([
                        lead.phone,
                        lead.status,
                        lead.has_interest,
                        ", ".join(lead.crops),
                        lead.volume,
                        lead.region,
                        lead.basis,
                        lead.harvest_time,
                        lead.contact_name,
                        lead.notes,
                        lead.created_at
                    ])
            
            logger.info(f"Exported {len(leads)} leads to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export leads: {e}")


# Глобальный экземпляр
_lead_storage: Optional[LeadStorage] = None


def get_lead_storage() -> LeadStorage:
    """Получить глобальный экземпляр хранилища лидов."""
    global _lead_storage
    if _lead_storage is None:
        from .config import LEADS_DB_PATH
        _lead_storage = LeadStorage(LEADS_DB_PATH)
    return _lead_storage
