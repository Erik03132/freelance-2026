import aiosqlite
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "crm.db"


async def get_db():
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT '',
            phone TEXT NOT NULL DEFAULT '',
            company_name TEXT NOT NULL DEFAULT '',
            region TEXT NOT NULL DEFAULT '',
            contact_name TEXT NOT NULL DEFAULT '',
            product TEXT NOT NULL DEFAULT '',
            volume TEXT NOT NULL DEFAULT '',
            ready_date TEXT NOT NULL DEFAULT '',
            price_info TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'other',
            notes TEXT NOT NULL DEFAULT '',
            transcript TEXT NOT NULL DEFAULT '',
            recording_id TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL DEFAULT '',
            due_date TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            created TEXT NOT NULL DEFAULT '',
            done INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
        CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
        CREATE INDEX IF NOT EXISTS idx_contacts_created ON contacts(created_at);
        CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(due_date);
        CREATE INDEX IF NOT EXISTS idx_reminders_done ON reminders(done);
        CREATE TABLE IF NOT EXISTS call_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL DEFAULT '',
            company_name TEXT NOT NULL DEFAULT '',
            contact_name TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_queue_status ON call_queue(status);
    """)
    await db.commit()
    await db.close()
