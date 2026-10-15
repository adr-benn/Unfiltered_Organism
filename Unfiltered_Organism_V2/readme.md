# Unfiltered Organism v2 🧬

An enterprise-ready, bare-metal autonomous self-correction framework designed for resilient script generation, multi-file orchestration, and self-evolution.

---

## ⚡ What's New in v2

Version 2 introduces critical structural refactoring and stability improvements to address broken execution loops and unfunctional main entry points:

* **Engine Routing Isolation (`engine.py`)**: Completely decoupled LLM communication into a robust, multi-provider engine supporting local Ollama weights as well as cloud-based fallback routes (Claude, Gemini, OpenAI) with configurable temperature control.
* **Strict Governor Control Loop (`main.py`)**: Fixed unfunctional state tracking in the main loop. The governor now cleanly manages execution retries, dynamic timeouts, and communicates cleanly with sandbox targets without raising unbound local errors.
* **Enhanced Mutation Watchdog**: Upgraded error signature tracking. If the agent hits a repeating error twice in a row, a hard system override forces a structural rewrite rather than falling into an infinite loop of identical failures.
* **Pluggable Persistence (`memory_vault/storage_driver.py`)**: Cleaned up modular file I/O and keyword relevance scoring to fetch past successful code blueprints more efficiently.

---

## 📂 Project Structure

unfiltered_organism/
│
├── main.py                  # The blind control loop (Strict Governor)[cite: 4]
├── engine.py                # Isolated LLM communication layer[cite: 4]
├── config.json              # Operational constraints (Timeouts, tick limits)[cite: 1, 4]
├── requirements.txt         # Bare essentials (`requests`, `pydantic`)[cite: 5]
│
├── memory_vault/            # Persistent storage for successful code blueprints[cite: 4]
│   └── storage_driver.py    # Pluggable persistence & metrics interface[cite: 6]
│
├── logs/                    # Execution telemetry & audit trails[cite: 4]
│   └── metrics_vault.jsonl  # Token metrics, errors, and tracebacks[cite: 4]
│
└── sandbox_workspace/       # Active execution and sandbox test targets
---

## 🚀 Quickstart

1. **Clone & Setup Environment:**
   ```bash
   git clone [https://github.com/yourusername/unfiltered_organism.git](https://github.com/yourusername/unfiltered_organism.git)
   cd unfiltered_organism
   pip install -r requirements.txt

2. Ensure Local Engine is Running:
   Make sure your local Ollama instance is active:

   ollama run qwen2.5-coder:14b-instruct-q4_K_M

3. Deploy the Organism:

   python main.py