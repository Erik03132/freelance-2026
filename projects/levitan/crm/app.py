import json
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import jinja2
from fastapi import FastAPI, Request, Query, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from crm.database import get_db, init_db

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR.parent / "data" / "call_results"

app = FastAPI(title="Levitan CRM", version="1.0.0")
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True,
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

STATUS_LABELS = {
    "lead": "лид",
    "callback": "перезвонить",
    "rejected": "отказ",
    "no_interest": "не интересно",
    "no_answer": "не ответил",
    "no_contact": "нет контакта",
    "other": "другое",
    "overdue": "просрочено",
}


def render(name: str, **context):
    context.setdefault("status_labels", STATUS_LABELS)
    t = jinja_env.get_template(name)
    return HTMLResponse(t.render(**context))


# === PYDANTIC MODELS ===

class ContactCreate(BaseModel):
    timestamp: str = ""
    phone: str = ""
    company_name: str = ""
    region: str = ""
    contact_name: str = ""
    product: str = ""
    volume: str = ""
    ready_date: str = ""
    price_info: str = ""
    status: str = "other"
    notes: str = ""
    transcript: str = ""
    recording_id: str = ""


class ContactUpdate(BaseModel):
    timestamp: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    region: Optional[str] = None
    contact_name: Optional[str] = None
    product: Optional[str] = None
    volume: Optional[str] = None
    ready_date: Optional[str] = None
    price_info: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    transcript: Optional[str] = None
    recording_id: Optional[str] = None


class ReminderCreate(BaseModel):
    phone: str = ""
    due_date: str = ""
    note: str = ""


class QueueAdd(BaseModel):
    phone: str
    company_name: str = ""
    contact_name: str = ""
    note: str = ""


# === WEB ROUTES ===

@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    db = await get_db()
    total = (await (await db.execute("SELECT COUNT(*) FROM contacts")).fetchone())[0]
    leads = (await (await db.execute("SELECT COUNT(*) FROM contacts WHERE status='lead'")).fetchone())[0]
    today = date.today().isoformat()

    today_calls = (await (await db.execute(
        "SELECT COUNT(*) FROM contacts WHERE date(timestamp)=? AND timestamp != ''", (today,)
    )).fetchone())[0]

    pending = (await (await db.execute(
        "SELECT COUNT(*) FROM reminders WHERE done=0 AND due_date>=?",
        (today,)
    )).fetchone())[0]
    overdue = (await (await db.execute(
        "SELECT COUNT(*) FROM reminders WHERE done=0 AND due_date<?",
        (today,)
    )).fetchone())[0]

    cur = await db.execute(
        "SELECT status, COUNT(*) as cnt FROM contacts GROUP BY status ORDER BY cnt DESC"
    )
    status_rows = await cur.fetchall()
    status_chart = {r["status"]: r["cnt"] for r in status_rows}

    cur = await db.execute(
        "SELECT id, phone, company_name, contact_name, status, created_at "
        "FROM contacts ORDER BY created_at DESC LIMIT 10"
    )
    recent_rows = await cur.fetchall()
    queue_count = (await (await db.execute("SELECT COUNT(*) FROM call_queue")).fetchone())[0]
    await db.close()

    return render("dashboard.html",
        request=request,
        total=total,
        leads=leads,
        today_calls=today_calls,
        queue_count=queue_count,
        pending_reminders=pending,
        overdue_reminders=overdue,
        status_chart=status_chart,
        recent_contacts=[dict(r) for r in recent_rows],
    )


@app.get("/contacts", response_class=HTMLResponse)
async def contacts_page(
    request: Request,
    page: int = 1,
    per_page: int = 50,
    search: str = "",
    status: str = "",
):
    db = await get_db()
    conditions = []
    params = []
    if search:
        conditions.append(
            "(phone LIKE ? OR company_name LIKE ? OR contact_name LIKE ? OR notes LIKE ?)"
        )
        like = f"%{search}%"
        params.extend([like, like, like, like])
    if status:
        conditions.append("status=?")
        params.append(status)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    offset = (page - 1) * per_page

    count_row = await db.execute(f"SELECT COUNT(*) FROM contacts {where}", params)
    total = (await count_row.fetchone())[0]

    rows = await db.execute(
        f"SELECT * FROM contacts {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, offset],
    )
    contacts = [dict(r) for r in await rows.fetchall()]
    await db.close()

    pages = max(1, (total + per_page - 1) // per_page)
    return render("contacts.html",
        request=request,
        contacts=contacts,
        page=page,
        pages=pages,
        total=total,
        search=search,
        status_filter=status,
        statuses=["lead", "callback", "rejected", "no_interest", "no_answer", "no_contact", "other"],
    )


@app.get("/contacts/{contact_id}", response_class=HTMLResponse)
async def contact_detail(request: Request, contact_id: int):
    db = await get_db()
    row = await db.execute("SELECT * FROM contacts WHERE id=?", (contact_id,))
    contact = await row.fetchone()
    await db.close()
    if not contact:
        return HTMLResponse("Contact not found", status_code=404)
    return render("contact_detail.html",
        request=request,
        c=dict(contact),
    )


@app.get("/reminders", response_class=HTMLResponse)
async def reminders_page(request: Request):
    db = await get_db()
    today = date.today().isoformat()
    active = await db.execute(
        "SELECT * FROM reminders WHERE done=0 ORDER BY due_date ASC"
    )
    done_rows = await db.execute(
        "SELECT * FROM reminders WHERE done=1 ORDER BY due_date DESC LIMIT 50"
    )
    active_reminders = [dict(r) for r in await active.fetchall()]
    done_reminders = [dict(r) for r in await done_rows.fetchall()]
    await db.close()
    return render("reminders.html",
        request=request,
        active=active_reminders,
        done=done_reminders,
        today=today,
    )


@app.get("/today", response_class=HTMLResponse)
async def today_page(request: Request):
    db = await get_db()
    today = date.today().isoformat()
    # Reminders due today or overdue
    cur = await db.execute(
        "SELECT * FROM reminders WHERE done=0 AND due_date<=? ORDER BY due_date ASC",
        (today,)
    )
    due_reminders = [dict(r) for r in await cur.fetchall()]
    # Manually added queue items
    cur = await db.execute("SELECT * FROM call_queue ORDER BY created_at DESC")
    queue = [dict(r) for r in await cur.fetchall()]
    overdue = len([r for r in due_reminders if r["due_date"] < today])
    await db.close()
    return render("today.html",
        request=request,
        due_reminders=due_reminders,
        queue=queue,
        overdue=overdue,
        today=today,
    )


@app.get("/import", response_class=HTMLResponse)
async def import_page(request: Request, message: str = ""):
    files = sorted(DATA_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
    return render("import.html",
        request=request,
        files=[f.name for f in files],
        message=message,
    )


# === API ROUTES ===

@app.get("/api/stats")
async def api_stats():
    db = await get_db()
    total = (await (await db.execute("SELECT COUNT(*) FROM contacts")).fetchone())[0]
    leads = (await (await db.execute("SELECT COUNT(*) FROM contacts WHERE status='lead'")).fetchone())[0]
    today = date.today().isoformat()
    today_calls = (await (await db.execute(
        "SELECT COUNT(*) FROM contacts WHERE date(timestamp)=? AND timestamp != ''", (today,)
    )).fetchone())[0]
    await db.close()
    return {"total": total, "leads": leads, "today_calls": today_calls}


@app.get("/api/contacts")
async def api_contacts(search: str = "", status: str = "", limit: int = 100, offset: int = 0):
    db = await get_db()
    conditions = []
    params = []
    if search:
        conditions.append("(phone LIKE ? OR company_name LIKE ? OR contact_name LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])
    if status:
        conditions.append("status=?")
        params.append(status)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = await db.execute(
        f"SELECT * FROM contacts {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    )
    contacts = [dict(r) for r in await rows.fetchall()]
    await db.close()
    return contacts


@app.get("/api/contacts/{contact_id}")
async def api_get_contact(contact_id: int):
    db = await get_db()
    row = await db.execute("SELECT * FROM contacts WHERE id=?", (contact_id,))
    contact = await row.fetchone()
    await db.close()
    if not contact:
        raise HTTPException(404, "Contact not found")
    return dict(contact)


@app.post("/api/contacts", status_code=201)
async def api_create_contact(data: ContactCreate):
    now = datetime.now().isoformat()
    db = await get_db()
    cur = await db.execute(
        """INSERT INTO contacts
        (timestamp, phone, company_name, region, contact_name, product,
         volume, ready_date, price_info, status, notes, transcript, recording_id,
         created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data.timestamp, data.phone, data.company_name, data.region,
         data.contact_name, data.product, data.volume, data.ready_date,
         data.price_info, data.status, data.notes, data.transcript,
         data.recording_id, now, now),
    )
    await db.commit()
    contact_id = cur.lastrowid
    await db.close()
    return {"id": contact_id, **data.model_dump()}


@app.put("/api/contacts/{contact_id}")
async def api_update_contact(contact_id: int, data: ContactUpdate):
    now = datetime.now().isoformat()
    db = await get_db()
    existing = await db.execute("SELECT * FROM contacts WHERE id=?", (contact_id,))
    row = await existing.fetchone()
    if not row:
        await db.close()
        raise HTTPException(404, "Contact not found")
    updates = data.model_dump(exclude_none=True)
    if not updates:
        await db.close()
        return dict(row)
    updates["updated_at"] = now
    set_clause = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [contact_id]
    await db.execute(
        f"UPDATE contacts SET {set_clause} WHERE id=?", values
    )
    await db.commit()
    row = await (await db.execute("SELECT * FROM contacts WHERE id=?", (contact_id,))).fetchone()
    await db.close()
    return dict(row)


@app.delete("/api/contacts/{contact_id}")
async def api_delete_contact(contact_id: int):
    db = await get_db()
    await db.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    await db.commit()
    await db.close()
    return {"ok": True}


@app.get("/api/reminders")
async def api_reminders(done: Optional[int] = None):
    db = await get_db()
    if done is not None:
        rows = await db.execute(
            "SELECT * FROM reminders WHERE done=? ORDER BY due_date ASC", (done,)
        )
    else:
        rows = await db.execute("SELECT * FROM reminders ORDER BY due_date ASC")
    reminders = [dict(r) for r in await rows.fetchall()]
    await db.close()
    return reminders


@app.post("/api/reminders", status_code=201)
async def api_create_reminder(data: ReminderCreate):
    now = datetime.now().isoformat()
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO reminders (phone, due_date, note, created, done) VALUES (?,?,?,?,0)",
        (data.phone, data.due_date, data.note, now),
    )
    await db.commit()
    reminder_id = cur.lastrowid
    await db.close()
    return {"id": reminder_id, **data.model_dump(), "created": now, "done": False}


@app.patch("/api/reminders/{reminder_id}/done")
async def api_toggle_reminder(reminder_id: int):
    db = await get_db()
    row = await db.execute("SELECT * FROM reminders WHERE id=?", (reminder_id,))
    r = await row.fetchone()
    if not r:
        await db.close()
        raise HTTPException(404, "Reminder not found")
    new_done = 0 if r["done"] else 1
    await db.execute("UPDATE reminders SET done=? WHERE id=?", (new_done, reminder_id))
    await db.commit()
    await db.close()
    return {"id": reminder_id, "done": bool(new_done)}


@app.delete("/api/reminders/{reminder_id}")
async def api_delete_reminder(reminder_id: int):
    db = await get_db()
    await db.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    await db.commit()
    await db.close()
    return {"ok": True}


@app.post("/api/import")
async def api_import(filename: str = Query(...)):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, f"File not found: {filename}")
    with open(filepath) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise HTTPException(400, "Expected JSON array")
    now = datetime.now().isoformat()
    db = await get_db()
    imported = 0
    for item in data:
        ts = item.get("timestamp", now)
        await db.execute(
            """INSERT INTO contacts
            (timestamp, phone, company_name, region, contact_name, product,
             volume, ready_date, price_info, status, notes, transcript,
             recording_id, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (ts, item.get("phone", ""), item.get("company_name", ""),
             item.get("region", ""), item.get("contact_name", ""),
             item.get("product", ""), item.get("volume", ""),
             item.get("ready_date", ""), item.get("price_info", ""),
             item.get("status", "other"), item.get("notes", ""),
             item.get("transcript", ""), item.get("recording_id", ""),
             now, now),
        )
        imported += 1
    await db.commit()
    await db.close()
    return {"imported": imported, "file": filename}


# === QUEUE API ===

@app.get("/api/queue")
async def api_queue():
    db = await get_db()
    cur = await db.execute("SELECT * FROM call_queue ORDER BY created_at DESC")
    items = [dict(r) for r in await cur.fetchall()]
    await db.close()
    return items


@app.post("/api/queue", status_code=201)
async def api_queue_add(data: QueueAdd):
    now = datetime.now().isoformat()
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO call_queue (phone, company_name, contact_name, note, status, created_at) VALUES (?,?,?,?,?,?)",
        (data.phone, data.company_name, data.contact_name, data.note, "pending", now),
    )
    await db.commit()
    qid = cur.lastrowid
    await db.close()
    return {"id": qid, "phone": data.phone, "company_name": data.company_name, "note": data.note, "created_at": now}


@app.patch("/api/queue/{qid}/done")
async def api_queue_done(qid: int):
    db = await get_db()
    await db.execute("DELETE FROM call_queue WHERE id=?", (qid,))
    await db.commit()
    await db.close()
    return {"ok": True}


@app.delete("/api/queue/{qid}")
async def api_queue_delete(qid: int):
    db = await get_db()
    await db.execute("DELETE FROM call_queue WHERE id=?", (qid,))
    await db.commit()
    await db.close()
    return {"ok": True}


# === MAIN ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("crm.app:app", host="0.0.0.0", port=8088, reload=True)
