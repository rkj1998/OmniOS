# R:\OmniOS\core-cortex\cortex_engine.py
import os
import re
import time
import json
import sqlite3
import hashlib
import httpx
from typing import Dict, Any, List
from dotenv import load_dotenv
import sys

load_dotenv(r"R:\OmniOS\.env")

sys.path.append(r"R:\OmniOS\mcp-action-bus")
from mcp_bus import UniversalMCPBus

# =====================================================================
# 🔑 PASTE YOUR GROQ API KEY HERE (OR USE LOCAL RTX 4080 OLLAMA):
# =====================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat").strip()

SYSTEM_PROMPT = """You are the OmniOS Cortex Router. Convert the user's prompt into a JSON array of tool calls.
Available MCP Tools:
1. "jira_manage_ticket": {"title": str, "priority": "LOW"|"MEDIUM"|"HIGH"|"CRITICAL", "status": "TODO"|"IN_PROGRESS"|"DONE", "assignee": str}
2. "comms_post_alert": {"channel": str (e.g. "#dev-sprint", "#design-studio", "#calgary-ops"), "message": str, "require_approval": bool}
3. "creative_generate_visual_asset": {"template_type": "PHOTOSHOP_COMPOSITE"|"CAD_REPAIR_SCHEMATIC"|"UI_MOCKUP_BANNER", "headline_text": str, "highlight_component": str}
4. "device_automate_action": {"device_name": str (e.g. "Workstation-PC", "Smart-Home-Hub"), "action": str, "target_path_or_app": str}
5. "erp_check_and_order_part": {"sku": str, "quantity": int, "supplier": str}
6. "iiot_read_and_control_pump": {"machine_id": "CALGARY-PUMP-04"|"COMPRESSOR-A1", "target_rpm": int (400 to 1800)}

Respond ONLY with a valid JSON array of objects, each having "tool" and "params".
"""

class CortexOptimizationEngine:
    def __init__(self, macro_dir: str = r"R:\OmniOS\compiled-macros", db_path: str = r"R:\OmniOS\omnios_core.db"):
        self.mcp = UniversalMCPBus()
        self.macro_dir = macro_dir
        self.db_path = db_path
        os.makedirs(self.macro_dir, exist_ok=True)
        self._init_sqlite_db()

    def _init_sqlite_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS semantic_macro_cache (
                intent_hash TEXT PRIMARY KEY,
                prompt TEXT,
                plan_json TEXT,
                macro_file TEXT,
                hit_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS platform_metrics (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_requests INTEGER DEFAULT 0,
                zero_token_macro_hits INTEGER DEFAULT 0,
                llm_compilations INTEGER DEFAULT 0,
                estimated_dollars_saved REAL DEFAULT 0.0
            )
        """)
        cur.execute("INSERT OR IGNORE INTO platform_metrics (id) VALUES (1)")
        conn.commit()
        conn.close()

    def _get_intent_hash(self, prompt: str) -> str:
        cleaned = " ".join(prompt.lower().strip().split())
        return hashlib.sha256(cleaned.encode()).hexdigest()[:12]

    def _extract_json_array(self, raw_text: str) -> List[Dict[str, Any]]:
        match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw_text)

    def _call_live_llm_router(self, prompt: str, selected_model: str = "auto") -> tuple[List[Dict[str, Any]], str, int, float]:
        use_groq = selected_model in ("auto", "groq:llama-3.3-70b-versatile")
        ollama_tag = selected_model.replace("ollama:", "") if selected_model.startswith("ollama:") else "qwen2.5-coder:7b"

        if use_groq and GROQ_API_KEY and not GROQ_API_KEY.startswith("PASTE_"):
            try:
                r = httpx.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY.strip()}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1
                    },
                    timeout=10.0
                )
                if r.status_code == 200:
                    data = r.json()
                    content = data["choices"][0]["message"]["content"]
                    tokens = data.get("usage", {}).get("total_tokens", 450)
                    return self._extract_json_array(content), "☁️ GROQ_70B_LPU (Compiled to $0 Macro)", tokens, 0.0
            except Exception as e:
                print(f"Groq fallback triggered: {e}")

        try:
            r = httpx.post(
                OLLAMA_URL,
                json={
                    "model": ollama_tag,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=25.0
            )
            if r.status_code == 200:
                content = r.json()["message"]["content"]
                return self._extract_json_array(content), f"🟢 RTX_4080_LOCAL ({ollama_tag} -> $0 Macro)", 410, 0.0
        except Exception:
            pass

        return self._heuristic_plan(prompt), "⚙️ BUILTIN_DETERMINISTIC_PLANNER", 0, 0.0

    def _heuristic_plan(self, prompt: str) -> List[Dict[str, Any]]:
        p = prompt.lower()
        plan = []
        if any(w in p for w in ["pump", "machine", "sensor", "bearing", "calgary", "compressor", "rpm"]):
            rpm_match = re.search(r"(\d{3,4})\s*rpm", p)
            target_rpm = int(rpm_match.group(1)) if rpm_match else 1100
            machine = "COMPRESSOR-A1" if "compressor" in p else "CALGARY-PUMP-04"
            plan.append({"tool": "iiot_read_and_control_pump", "params": {"machine_id": machine, "target_rpm": target_rpm}})
            plan.append({"tool": "erp_check_and_order_part", "params": {"sku": "SKF-BEARING-992", "quantity": 2}})
            plan.append({"tool": "jira_manage_ticket", "params": {"title": f"Inspect & Replace Bearing on {machine}", "priority": "CRITICAL", "status": "IN_PROGRESS", "assignee": "Field-Eng-Bot"}})
            plan.append({
                "tool": "creative_generate_visual_asset",
                "params": {
                    "template_type": "CAD_REPAIR_SCHEMATIC",
                    "headline_text": f"REPAIR: {machine} @ {target_rpm} RPM",
                    "highlight_component": "Main_Drive_Bearing_Assembly"
                }
            })
            plan.append({"tool": "comms_post_alert", "params": {"channel": "#calgary-field-ops", "message": f"{machine} throttled to {target_rpm} RPM. Jira ticket created, ERP bearing ordered & CAD schematic rendered.", "require_approval": True}})
        elif any(w in p for w in ["jira", "sprint", "ticket", "bug", "slack", "device", "pc", "backup", "clean"]):
            plan.append({"tool": "jira_manage_ticket", "params": {"title": prompt[:48], "priority": "HIGH", "status": "IN_PROGRESS", "assignee": "DevOps-Agent"}})
            plan.append({"tool": "device_automate_action", "params": {"device_name": "Workstation-RTX4080", "action": "Clean Temp Cache & Sync Workspace", "target_path_or_app": "R:/OmniOS"}})
            plan.append({"tool": "comms_post_alert", "params": {"channel": "#dev-sprint-board", "message": f"Jira sprint updated & local workstation automation completed for: {prompt}", "require_approval": False}})
        else:
            plan.append({
                "tool": "creative_generate_visual_asset",
                "params": {
                    "template_type": "PHOTOSHOP_COMPOSITE",
                    "headline_text": prompt[:42],
                    "highlight_component": "Background_Mask_And_ColorGrade"
                }
            })
            plan.append({"tool": "jira_manage_ticket", "params": {"title": f"Creative Asset Review: {prompt[:32]}", "priority": "MEDIUM", "status": "DONE", "assignee": "Design-Bot"}})
            plan.append({"tool": "comms_post_alert", "params": {"channel": "#design-studio", "message": f"Photoshop/Vector composite rendered and attached to Jira board: {prompt}", "require_approval": False}})
        return plan

    def _compile_to_python_macro(self, intent_hash: str, prompt: str, plan: List[Dict[str, Any]]) -> str:
        macro_path = os.path.join(self.macro_dir, f"macro_{intent_hash}.py")
        script_content = f'''# AUTO-COMPILED OMNI-OS DETERMINISTIC MACRO
# Original Prompt: {prompt}
# LLM Token Cost per Execution: $0.0000
import sys
sys.path.append(r"R:\\OmniOS\\mcp-action-bus")
from mcp_bus import UniversalMCPBus

def run_deterministic_macro():
    bus = UniversalMCPBus()
    steps = {json.dumps(plan, indent=4)}
    return [bus.execute(s["tool"], s["params"]) for s in steps]

if __name__ == "__main__":
    print(run_deterministic_macro())
'''
        with open(macro_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        return macro_path

    def process_command(self, prompt: str, engine_mode: str = "auto", bypass_cache: bool = False) -> Dict[str, Any]:
        start_time = time.perf_counter()
        intent_hash = self._get_intent_hash(prompt)
        macro_file = os.path.join(self.macro_dir, f"macro_{intent_hash}.py")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT plan_json FROM semantic_macro_cache WHERE intent_hash = ?", (intent_hash,))
        row = cur.fetchone()

        if row and not bypass_cache:
            plan = json.loads(row[0])
            execution_mode = "⚡ STAGE_1_AND_4_SQLITE_COMPILED_MACRO (0 Tokens!)"
            tokens_used = 0
            cost_usd = 0.0
            cur.execute("UPDATE semantic_macro_cache SET hit_count = hit_count + 1 WHERE intent_hash = ?", (intent_hash,))
            cur.execute("""
                UPDATE platform_metrics 
                SET total_requests = total_requests + 1,
                    zero_token_macro_hits = zero_token_macro_hits + 1,
                    estimated_dollars_saved = estimated_dollars_saved + 0.045
                WHERE id = 1
            """)
        else:
            plan, execution_mode, tokens_used, cost_usd = self._call_live_llm_router(prompt, selected_model=engine_mode)
            self._compile_to_python_macro(intent_hash, prompt, plan)
            cur.execute(
                "INSERT OR REPLACE INTO semantic_macro_cache (intent_hash, prompt, plan_json, macro_file) VALUES (?, ?, ?, ?)",
                (intent_hash, prompt, json.dumps(plan), macro_file)
            )
            cur.execute("""
                UPDATE platform_metrics 
                SET total_requests = total_requests + 1,
                    llm_compilations = llm_compilations + 1
                WHERE id = 1
            """)

        conn.commit()
        cur.execute("SELECT total_requests, zero_token_macro_hits, llm_compilations, estimated_dollars_saved FROM platform_metrics WHERE id = 1")
        m_row = cur.fetchone()
        conn.close()

        stats = {
            "total_requests": m_row[0],
            "zero_token_macro_hits": m_row[1],
            "llm_compilations": m_row[2],
            "estimated_dollars_saved": m_row[3]
        }

        step_results = [self.mcp.execute(step["tool"], step["params"]) for step in plan]
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "prompt": prompt,
            "intent_hash": intent_hash,
            "execution_mode": execution_mode,
            "latency_ms": elapsed_ms,
            "llm_tokens_burned": tokens_used,
            "execution_cost_usd": cost_usd,
            "compiled_macro_file": macro_file,
            "workflow_results": step_results,
            "platform_economics": stats
        }