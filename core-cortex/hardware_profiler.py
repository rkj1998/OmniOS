# R:\OmniOS\core-cortex\hardware_profiler.py
import subprocess
import platform
import psutil
import httpx
from typing import Dict, Any, List

MODEL_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "groq:llama-3.3-70b-versatile",
        "name": "Llama 3.3 70B Versatile (Groq Cloud LPU)",
        "provider": "groq",
        "vram_gb": 0.0,
        "speed_tps": 800,
        "agent_score": 96.5,
        "coding_score": 94.0,
        "efficiency_rating": "99/100 (Cloud Free Tier)",
        "tier": "Cloud Ultra-Fast",
        "best_for": "Instant 800 tok/s multi-department macro compilation with zero local hardware load."
    },
    {
        "id": "ollama:qwen2.5-coder:14b",
        "name": "Qwen 2.5 Coder 14B (Local Sovereign Pro)",
        "provider": "ollama",
        "vram_gb": 9.5,
        "speed_tps": 75,
        "agent_score": 94.8,
        "coding_score": 96.2,
        "efficiency_rating": "98/100 (12–16GB+ GPU)",
        "tier": "Heavy Local GPU",
        "best_for": "Best local model for RTX 4080 (16GB). Frontier-grade Python macro compilation & ERP/SCADA routing."
    },
    {
        "id": "ollama:qwen2.5-coder:7b",
        "name": "Qwen 2.5 Coder 7B (Local High-Speed Agent)",
        "provider": "ollama",
        "vram_gb": 4.7,
        "speed_tps": 130,
        "agent_score": 91.5,
        "coding_score": 92.0,
        "efficiency_rating": "99/100 (Best VRAM/Speed Ratio)",
        "tier": "Mid/High Local GPU",
        "best_for": "Blazing 130 tok/s on RTX 4080 while using <30% VRAM. Ideal 24/7 background agent brain."
    },
    {
        "id": "ollama:glm4:9b",
        "name": "GLM-4 9B Chat (Tsinghua KEG Architecture)",
        "provider": "ollama",
        "vram_gb": 6.2,
        "speed_tps": 105,
        "agent_score": 90.8,
        "coding_score": 88.5,
        "efficiency_rating": "94/100 (8GB+ GPU)",
        "tier": "Mid/High Local GPU",
        "best_for": "Tsinghua GLM architecture. Great for enterprise ERP synthesis, docs, and structured tool calling."
    },
    {
        "id": "ollama:deepseek-r1:14b",
        "name": "DeepSeek-R1 14B Distill (Reasoning & Quant)",
        "provider": "ollama",
        "vram_gb": 9.2,
        "speed_tps": 72,
        "agent_score": 93.0,
        "coding_score": 95.4,
        "efficiency_rating": "96/100 (12–16GB+ GPU)",
        "tier": "Heavy Local GPU",
        "best_for": "Deep mathematical reasoning for Quant Commodity Hedging & complex Calgary IIoT failure physics."
    },
    {
        "id": "ollama:qwen2.5:3b",
        "name": "Qwen 2.5 3B (Laptop AI-Core / NPU / Edge Box)",
        "provider": "ollama",
        "vram_gb": 2.1,
        "speed_tps": 210,
        "agent_score": 83.0,
        "coding_score": 81.5,
        "efficiency_rating": "100/100 (Ultra-Light Edge/NPU)",
        "tier": "Laptop NPU / Edge IoT",
        "best_for": "Runs on any employee laptop (Intel Core Ultra / Ryzen AI NPU) or Calgary Factory Edge Gateway box."
    }
]

def detect_local_hardware() -> Dict[str, Any]:
    cpu_name = platform.processor() or "x86_64 Multi-Core Processor"
    cpu_cores = psutil.cpu_count(logical=True)
    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)

    gpu_name = "Integrated / CPU-NPU Mode"
    vram_gb = 0.0
    has_nvidia = False

    # Query NVIDIA GPU via nvidia-smi
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            encoding="utf-8",
            timeout=3
        ).strip()
        if out:
            parts = out.split(",")
            gpu_name = parts[0].strip()
            vram_gb = round(float(parts[1].strip()) / 1024.0, 1)
            has_nvidia = True
    except Exception:
        pass

    # Detect installed Ollama models
    installed_ollama = []
    ollama_online = False
    try:
        r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=1.5)
        if r.status_code == 200:
            ollama_online = True
            installed_ollama = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass

    # Compute personalized recommendations based on detected VRAM & RAM
    recommendations = []
    for m in MODEL_CATALOG:
        model_copy = dict(m)
        tag = m["id"].replace("ollama:", "")
        model_copy["installed"] = True if m["provider"] == "groq" else (tag in installed_ollama)

        if m["provider"] == "groq":
            model_copy["compatibility"] = "☁️ CLOUD READY (0 GB Local VRAM)"
            model_copy["recommended_badge"] = "⚡ Best Instant Cloud Speed"
        elif has_nvidia and vram_gb >= m["vram_gb"] + 2.0:
            model_copy["compatibility"] = f"🟢 OPTIMAL ON YOUR {gpu_name} ({m['vram_gb']}GB / {vram_gb}GB VRAM)"
            if m["id"] == "ollama:qwen2.5-coder:14b" and vram_gb >= 14.0:
                model_copy["recommended_badge"] = "🏆 #1 Recommended Local Pro (RTX 4080 Match)"
            elif m["id"] == "ollama:qwen2.5-coder:7b":
                model_copy["recommended_badge"] = "⭐ Best Daily Driver (Fastest + Low VRAM)"
            else:
                model_copy["recommended_badge"] = "✅ Fits 100% in GPU VRAM"
        elif ram_gb >= m["vram_gb"] * 1.5:
            model_copy["compatibility"] = f"🟡 RUNS ON SYSTEM RAM / NPU ({ram_gb}GB RAM)"
            model_copy["recommended_badge"] = "💻 Good for Laptop NPU / CPU" if m["vram_gb"] <= 3.0 else "⚠️ Partial CPU Offload"
        else:
            model_copy["compatibility"] = "🔴 INSUFFICIENT HARDWARE MEMORY"
            model_copy["recommended_badge"] = "❌ Not Recommended"

        recommendations.append(model_copy)

    return {
        "gpu_name": gpu_name,
        "vram_gb": vram_gb,
        "cpu_cores": cpu_cores,
        "ram_gb": ram_gb,
        "ollama_online": ollama_online,
        "installed_ollama_models": installed_ollama,
        "models": recommendations
    }