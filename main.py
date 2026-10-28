# R:\OmniOS\main.py
import os
import io
import csv
import sys
import sqlite3
import subprocess
import asyncio
import datetime
sys.path.append(r"R:\OmniOS\core-cortex")

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from cortex_engine import CortexOptimizationEngine
from hardware_profiler import detect_local_hardware

DB_PATH = r"R:\OmniOS\omnios_core.db"
HTML_PATH = r"R:\OmniOS\web-shell\index.html"
ASSETS_DIR = r"R:\OmniOS\compiled-macros"

app = FastAPI(title="OmniOS v5.0 Nova - Open-Source Cyber-Physical Environment OS")
cortex = CortexOptimizationEngine()
ACTIVE_DAEMONS = set()

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

class SlackApproveRequest(BaseModel):
    msg_id: int

class ScadaControlRequest(BaseModel):
    machine_id: str = "CALGARY-PUMP-04"
    target_rpm: int = 1100
    simulate_spike: bool = False

class StudioRenderRequest(BaseModel):
    template_type: str = "PHOTOSHOP_COMPOSITE"
    headline_text: str = "Omni-Studio Render"
    highlight_component: str = "Primary_Mask"
    contrast_boost: float = 1.35
    theme_color: str = "cyber"

class PackageToggleRequest(BaseModel):
    pkg_id: str

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

@app.post("/api/scada-control")
async def direct_scada_control(req: ScadaControlRequest):
    if req.simulate_spike:
        return cortex.mcp.execute("iiot_read_and_control_pump", {"machine_id": req.machine_id, "simulate_spike": True})
    return cortex.mcp.execute("iiot_read_and_control_pump", {"machine_id": req.machine_id, "target_rpm": req.target_rpm})

@app.post("/api/studio-render")
async def direct_studio_render(req: StudioRenderRequest):
    return cortex.mcp.execute("creative_generate_visual_asset", {
        "template_type": req.template_type,
        "headline_text": req.headline_text,
        "highlight_component": req.highlight_component,
        "contrast_boost": req.contrast_boost,
        "theme_color": req.theme_color
    })

@app.post("/api/pc-scan")
async def direct_pc_scan():
    return cortex.mcp.execute("device_automate_action", {
        "device_name": "Workstation-RTX4080",
        "action": "Instant Diagnostics & Workspace File Sort"
    })

@app.post("/api/toggle-package")
async def toggle_omni_package(req: PackageToggleRequest):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT installed, name FROM omni_packages WHERE pkg_id = ?", (req.pkg_id,))
    row = cur.fetchone()
    if row:
        new_val = 0 if row[0] == 1 else 1
        cur.execute("UPDATE omni_packages SET installed = ? WHERE pkg_id = ?", (new_val, req.pkg_id))
        conn.commit()
        cortex.mcp._log_status("OMNI_HUB", req.pkg_id, "INSTALLED" if new_val else "DISABLED", f"Package '{row[1]}' state updated")
    conn.close()
    return {"status": "ok"}

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
    conn.commit()
    conn.close()
    cortex.mcp._log_status("JIRA_BOARD", f"Ticket {req.ticket_key}", req.new_status, f"Status cycled to {req.new_status}")
    return {"status": "updated"}

@app.post("/api/jira-create")
async def manual_jira_create(req: JiraCreateRequest):
    return cortex.mcp.execute("jira_manage_ticket", {"title": req.title, "priority": req.priority, "status": "TODO", "assignee": "Human-Op"})

@app.post("/api/slack-post")
async def manual_slack_post(req: SlackPostRequest):
    return cortex.mcp.execute("comms_post_alert", {"channel": req.channel, "message": req.message, "require_approval": False})

@app.post("/api/slack-approve")
async def approve_slack_gate(req: SlackApproveRequest):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE comms_messages SET require_approval = 2 WHERE id = ?", (req.msg_id,))
    conn.commit()
    conn.close()
    cortex.mcp._log_status("ENTERPRISE_RBAC", f"Approval Gate #{req.msg_id}", "SIGNED_APPROVED", "Operator cryptographically approved action in Omni-Slack")
    return {"status": "approved"}

@app.get("/api/assets/{filename}")
async def serve_generated_asset(filename: str):
    fpath = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(fpath):
        return FileResponse(fpath)
    return {"error": "File not found"}

@app.get("/api/export-audit-csv")
async def export_compliance_audit_csv():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, created_at, module, action, status, details FROM system_status_logs ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Log_ID", "Timestamp", "Module", "Action_Target", "Status_Code", "Execution_Details"])
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=OmniOS_Compliance_Audit_Log.csv"}
    )

@app.get("/api/hardware-models")
async def get_hardware_and_models():
    return detect_local_hardware()

@app.get("/api/live-state")
async def get_live_system_state():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT ticket_key, title, assignee, priority, status, sprint, updated_at FROM jira_tickets ORDER BY rowid DESC LIMIT 8")
    tickets = [dict(zip(["key", "title", "assignee", "priority", "status", "sprint", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT machine_id, location, temp_c, vibration_mm_s, current_rpm, status FROM iiot_machines")
    machines = [dict(zip(["id", "location", "temp", "vib", "rpm", "status"], r)) for r in cur.fetchall()]

    cur.execute("SELECT po_number, sku, qty, total_cost, supplier, status, created_at FROM erp_purchase_orders ORDER BY rowid DESC LIMIT 6")
    pos = [dict(zip(["po", "sku", "qty", "cost", "supplier", "status", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT id, channel, message, require_approval, created_at FROM comms_messages ORDER BY id DESC LIMIT 8")
    msgs = [dict(zip(["id", "channel", "message", "approval", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT module, action, status, details, created_at FROM system_status_logs ORDER BY id DESC LIMIT 25")
    logs = [dict(zip(["module", "action", "status", "details", "time"], r)) for r in cur.fetchall()]

    cur.execute("SELECT pkg_id, name, category, version, description, installed FROM omni_packages")
    packages = [dict(zip(["id", "name", "category", "version", "desc", "installed"], r)) for r in cur.fetchall()]

    cur.execute("SELECT intent_hash, prompt, macro_file, hit_count FROM semantic_macro_cache ORDER BY rowid DESC")
    macros = [{"hash": r[0], "prompt": r[1], "file": r[2], "hits": r[3], "daemon_active": r[0] in ACTIVE_DAEMONS} for r in cur.fetchall()]

    cur.execute("SELECT zero_token_macro_hits, estimated_dollars_saved FROM platform_metrics WHERE id = 1")
    m_row = cur.fetchone() or (0, 0.0)
    conn.close()
    return {
        "tickets": tickets, "machines": machines, "purchase_orders": pos,
        "messages": msgs, "logs": logs, "packages": packages, "macros": macros,
        "zero_hits": m_row[0], "dollars_saved": m_row[1]
    }

@app.get("/")
async def serve_os_desktop():
    return FileResponse(HTML_PATH)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Launching OmniOS v5.0 Nova Spatial Environment on http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)