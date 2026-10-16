(*For owner Review)

# Execution Model

A quick walkthrough of how the harness runs code, for anyone getting oriented
with the project. Descriptive only.

## Execution path

Each tick of the governor loop (`main.py`):

1. `main.py` requests code from an LLM via `engine.py` (`query_model`).
2. The returned code is written to the sandbox target file
   (`examples/sandbox_target.py`, or `sandbox_file` in `config.json`).
3. The file is executed with:
   ```python
   subprocess.run([sys.executable, SANDBOX_TARGET_PATH],
                  capture_output=True, text=True, timeout=timeout_sec)
   ```
4. stdout, stderr, and the exit code are captured and logged to
   `logs/metrics_vault.jsonl`. Successful runs are saved to `memory_vault/`.

## Execution environment

- Generated code runs under the same Python interpreter, OS user, filesystem,
  and network access as the governor process.
- Runs are bounded by the `timeout_seconds` value from `config.json`.

## Model endpoints

- Default (local): Ollama at `http://localhost:11434`.
- Fallback routes selected by `MODEL_NAME`: Anthropic Claude, Google Gemini,
  OpenAI. These send mission and history text to the respective third-party API.

## Memory reuse

- Code from successful runs is stored in `memory_vault/` and re-injected into
  later prompts as reference ("verified working code") based on keyword matching.
