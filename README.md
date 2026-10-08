# Unfiltered Organism 🧬

> **A Note from the Creator:** 
> I built **Unfiltered Organism** out of frustration with how standard AI coding loops get stuck repeating the exact same broken logic. That kind of wasted time and token burn dictates where this technology, economy, and life are heading—so I wanted to build something for the people, for us to take back our digital freedom. It's a lightweight, local orchestrator that doesn't just retry blindly, but actively catches execution traps and forces itself to completely mutate its architecture from scratch. Running locally on Pop!_OS via Ollama, it combines a strict governance loop with persistent memory vaults and complete local control to keep everything secure and secluded.

---

> *From Trial-and-Error to Self-Evolution.*

**Unfiltered Organism** is an autonomous Python coding agent harness designed with a strict governance loop, a secure execution sandbox, and a self-reflection mechanism that forces architectural mutation when the agent gets trapped in repeating error loops.

---

## 🧠 The Core Mental Model

Imagine an old-school video game loop where a character tries to cross a bridge, falls into a pit, reads what went wrong, and tries a different approach until they win. That is the exact heartbeat of this framework, flowing seamlessly from a basic execution loop into a self-reflecting, evolving organism:

1. **The Boss (`main.py` - The Strict Governor):** The manager of the control loop. It enforces the rules, checks execution results, feeds errors back, and watches for traps.
2. **The Imagination Network (`engine.py` - The Smart Worker):** The LLM backend that acts as the creative engine, generating code ideas and adapting when the Boss hands back a traceback.
3. **The Sandbox (`sandbox_target.py` - The Runtime Workspace):** The isolated runtime environment where generated code is actually executed and tested live.
4. **The Toolkit (`tools/` - Modular Utilities):** The auxiliary helper scripts and utility functions used by the orchestrator and sandbox environment for environment checks and telemetry preprocessing.
5. **The Filing Cabinet (`memory_vault/` and `logs/`):** Logs execution metrics, token counts, and error traces while archiving successful historical blueprints for retrieval via RAG keyword matching.

### The Evolution & Mutation Trigger
Standard LLMs love to "bang their heads against a wall," generating the exact same flawed logic repeatedly when given a generic retry command. **Unfiltered Organism** features a built-in watchdog:
* **Error Signature Tracking:** Monitors tracebacks across execution ticks.
* **The Mutation Strike:** If the Boss sees the *exact same error message twice in a row*, it drops a hard system override into the conversation history, forcing the model to clear its cognitive cache and rewrite the entire script using a completely different architectural pattern.

---

## ⚙️ System Requirements

* **Operating System:** Pop!_OS (or Linux/macOS/Windows)
* **Python Version:** Python 3.10+
* **Local LLM Runner:** [Ollama](https://ollama.com/) installed and running locally
* **Recommended Model (and default setup):** `qwen2.5-coder:7b`

---

## 📦 Dependencies & Setup

The core project relies on Python standard libraries (`asyncio`, `subprocess`, `json`, `os`, `sys`, `time`, `datetime`, `urllib`), plus one external HTTP library for communication.

### 1. Verify or Install Python 3
Ensure Python 3 and pip are available on your system:
```bash
python3 --version
sudo apt update && sudo apt install python3 python3-pip

```

### 2. Install Python Dependencies

Install the required `requests` package via terminal:

```bash
pip install requests

```

### 3. Install and Configure Ollama

Make sure Ollama is installed locally, then pull the required coder model:

```bash
ollama pull qwen2.5-coder:7b

```

Verify that the Ollama background service is running at `http://localhost:11434`.

---

## 📁 Project Structure

Ensure your workspace contains the following files and directories:

```text
your_project_folder/
├── main.py
├── engine.py
├── storage_driver.py
├── config.json
├── sandbox_target.py
├── memory_vault/   (created automatically)
└── logs/           (created automatically)

```

---

## 🚀 How to Start and Use

1. **Run the Governor:**
Execute the core orchestrator script from your project directory:
```bash
python3 main.py

```


2. **Provide a Mission:**
* When prompted: `[*] What is the mission for the organism today? (Press Enter to use default async scanner):`
* **Press Enter** to run the default mission (an asynchronous Python network sweep utility utilizing `asyncio` and `socket`), or type a custom coding objective of your choice.


3. **Observe the Loop:**
* The organism ticks through generation, sandboxed execution (`sandbox_target.py`), and telemetry logging (`logs/metrics_vault.jsonl`).
* Successful runs automatically commit code snapshots to `memory_vault/`, while repeating errors trigger architectural mutations to clear execution traps.

---
---

### 📝 P.S. Developer Notes & Roadmap

* **Changing the Model:** If you want to use a different local model instead of `qwen2.5-coder:7b`, you can update `MODEL_NAME` in `engine.py` or change the `"model"` string directly in `main.py`.
* **Adjusting Limits:** Operational limits like maximum execution ticks (default is 15) and sandbox timeouts can be easily configured inside `config.json` or adjusted directly at the top of `main.py`.
* **The Persona:** Currently, the system prompt hardcodes the organism to act as an elite network engineer (tailored for tasks like async network sweeps). I am actively working on refactoring this to make the persona fully dynamic.
* **Next Goal (Decoupling & Generalization):** My next major milestone is to **decouple the execution logic from the hardcoded parameters and system prompts**, allowing this harness to be easily translated into other use cases (like data analysis, web scraping, or cybersecurity auditing) without rewriting the core loop. *If you have ideas or want to collaborate on structuring a clean configuration loader for multiple use cases, contributions, forks, and pull requests are more than welcome!*

> **P.S.S.** Thanks for stopping by and checking out the repository! This is the first major project I'm working on, so any feedback, ideas, or discussions are always welcome. Feel free to reach out!

```

```