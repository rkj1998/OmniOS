# R:\OmniOS\main.py
import os
import sys
import sqlite3
import subprocess
import asyncio
import datetime
sys.path.append(r"R:\OmniOS\core-cortex")

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from cortex_engine import CortexOptimizationEngine
from hardware_profiler import detect_local_hardware

DB_PATH = r"R:\OmniOS\omnios_core.db"
HTML_PATH = r"R:\OmniOS\web-shell\index.html"

app = FastAPI(title="OmniOS v4.0 - Open-Source Cyber-Physical Environment OS")
cortex = CortexOptimizationEngine()
ACTIVE_DAEMONS = set()

def ensure_all_v4_tables_exist():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_status_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT, action TEXT, status TEXT, details TEXT, created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jira_tickets (
            ticket_key TEXT PRIMARY KEY,
            title TEXT, assignee TEXT, priority TEXT, status TEXT, sprint TEXT, updated_at TEXT
        )
    """)
    cur.execute("SELECT COUNT(*) FROM jira_tickets")
    if cur.fetchone()[0] == 0:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cur.executemany("INSERT INTO jira_tickets VALUES (?, ?, ?, ?, ?, ?, ?)", [
            ("OMNI-101", "Integrate Photoshop Layer Mask AI Pipeline", "Design-Agent", "HIGH", "IN_PROGRESS", "Sprint-4", now),
            ("OMNI-102", "Calgary Plant Pump #4 Bearing Inspection", "Field-Bot-01", "CRITICAL", "TODO", "Sprint-4", now),
            ("OMNI-103", "Automate ERP Supplier Invoice Sync", "Ops-Agent", "MEDIUM", "DONE", "Sprint-4", now)
        ])
    cur.execute("SELECT COUNT(*) FROM system_status_logs")
    if cur.fetchone()[0] == 0:
        now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO system_status_logs (module, action, status, details, created_at) VALUES (?, ?, ?, ?, ?)",
            ("KERNEL_V4", "System Boot", "ONLINE", "OmniOS v4.0 Spatial Environment & Git Open-Core initialized.", now_s)
        )
    conn.commit()
    conn.close()

ensure_all_v4_tables_exist()

class PromptRequest(BaseModel):
    prompt: str
    engine_mode: str = "auto"
    bypass_cache: bool = False

class PullModelRequest(BaseModel):
    model_tag: str

class DaemonToggleRequest(BaseModel):
    intent_hash: str

class JiraStatusUpdate(BaseModel):
    ticket_key: str
    new_status: str

class JiraCreateRequest(BaseModel):
    title: str
    priority: str = "HIGH"

class SlackPostRequest(BaseModel):
    channel: str
    message: str

async def background_daemon_loop():
    while True:
        await asyncio.sleep(15)
        for intent_hash in list(ACTIVE_DAEMONS):
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT prompt FROM semantic_macro_cache WHERE intent_hash = ?", (intent_hash,))
                row = cur.fetchone()
                conn.close()
                if row:
                    cortex.process_command(row[0], engine_mode="auto", bypass_cache=False)
            except Exception as e:
                print(f"Daemon error: {e}")

@app.on_event("startup")
async def start_daemons():
    asyncio.create_task(background_daemon_loop())

@app.post("/api/command")
async def run_omni_command(req: PromptRequest):
    return cortex.process_command(req.prompt, req.engine_mode, req.bypass_cache)

@app.post("/api/pull-model")
async def pull_ollama_model(req: PullModelRequest):
    tag = req.model_tag.replace("ollama:", "")
    subprocess.Popen(["ollama", "pull", tag], creationflags=subprocess.CREATE_NEW_CONSOLE)
    return {"status": "started", "message": f"Opened terminal downloading {tag} to your RTX 4080!"}

@app.post("/api/toggle-daemon")
async def toggle_daemon(req: DaemonToggleRequest):
    if req.intent_hash in ACTIVE_DAEMONS:
        ACTIVE_DAEMONS.remove(req.intent_hash)
        return {"active": False}
    ACTIVE_DAEMONS.add(req.intent_hash)
    return {"active": True}

@app.post("/api/jira-status")
async def update_jira_ticket_status(req: JiraStatusUpdate):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE jira_tickets SET status = ? WHERE ticket_key = ?", (req.new_status, req.ticket_key))
    now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO system_status_logs (module, action, status, details, created_at) VALUES (?, ?, ?, ?, ?)",
        ("JIRA_BOARD", f"Ticket {req.ticket_key}", req.new_status, f"Status cycled to {req.new_status}", now_s)
    )
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.post("/api/jira-create")
async def manual_jira_create(req: JiraCreateRequest):
    return cortex.mcp.execute("jira_manage_ticket", {"title": req.title, "priority": req.priority, "status": "TODO", "assignee": "Human-Op"})

@app.post("/api/slack-post")
async def manual_slack_post(req: SlackPostRequest):
    return cortex.mcp.execute("comms_post_alert", {"channel": req.channel, "message": req.message, "require_approval": False})

@app.get("/api/hardware-models")
async def get_hardware_and_models():
    return detect_local_hardware()

@app.get("/api/live-state")
async def get_live_system_state():
    ensure_all_v4_tables_exist()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT ticket_key, title, assignee, priority, status, sprint, updated_at FROM jira_tickets ORDER BY rowid DESC LIMIT 8")
    tickets = [dict(zip(["key", "title", "assignee", "priority", "status", "sprint", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT machine_id, location, temp_c, vibration_mm_s, current_rpm, status FROM iiot_machines")
    machines = [dict(zip(["id", "location", "temp", "vib", "rpm", "status"], r)) for r in cur.fetchall()]

    cur.execute("SELECT po_number, sku, qty, total_cost, supplier, status, created_at FROM erp_purchase_orders ORDER BY rowid DESC LIMIT 6")
    pos = [dict(zip(["po", "sku", "qty", "cost", "supplier", "status", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT channel, message, require_approval, created_at FROM comms_messages ORDER BY id DESC LIMIT 8")
    msgs = [dict(zip(["channel", "message", "approval", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT module, action, status, details, created_at FROM system_status_logs ORDER BY id DESC LIMIT 20")
    logs = [dict(zip(["module", "action", "status", "details", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT intent_hash, prompt, macro_file, hit_count FROM semantic_macro_cache ORDER BY rowid DESC")
    macros = [{"hash": r[0], "prompt": r[1], "file": r[2], "hits": r[3], "daemon_active": r[0] in ACTIVE_DAEMONS} for r in cur.fetchall()]

    cur.execute("SELECT zero_token_macro_hits, estimated_dollars_saved FROM platform_metrics WHERE id = 1")
    m_row = cur.fetchone() or (0, 0.0)
    conn.close()
    return {
        "tickets": tickets, "machines": machines, "purchase_orders": pos,
        "messages": msgs, "logs": logs, "macros": macros,
        "zero_hits": m_row[0], "dollars_saved": m_row[1]
    }

@app.get("/")
async def serve_os_desktop():
    return FileResponse(HTML_PATH)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Launching OmniOS Environment v4.0 on http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)