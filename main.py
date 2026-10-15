import os
import sys
import json
import time
import subprocess
from datetime import datetime
from engine import query_model

# ---------------------------------------------------------
# 1. LOAD CONFIGURATION FROM nested config.json
# ---------------------------------------------------------
CONFIG_PATH = "config.json"
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except Exception:
        config = {}
else:
    config = {}

agent_params = config.get("agent_parameters", {})
target_config = config.get("target_configuration", {})

MAX_TICKS = agent_params.get("max_ticks", 15)
DEFAULT_TIMEOUT = agent_params.get("default_timeout_seconds", 30)
TIMEOUT_INCREMENT = agent_params.get("timeout_increment_seconds", 30)
TEMPERATURE = agent_params.get("temperature", 0.2)
SANDBOX_TARGET_PATH = target_config.get("sandbox_file", "examples/sandbox_target.py")

os.makedirs("memory_vault", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("examples", exist_ok=True)


# ---------------------------------------------------------
# 2. DEFAULT PRESET MISSIONS
# ---------------------------------------------------------
DEFAULT_MISSIONS = {
    "1": "Write an advanced asynchronous Python script using 'asyncio' and 'socket' that performs a high-speed network sweep across local subnet range 30.30.30.1 to 30.30.30.50 for core management ports (22, 80, 443, 8006), measures RTT in milliseconds, and outputs a valid JSON array.",
    "2": "Write a Python script that checks system resource utilization (CPU, memory, disk space) and outputs the metrics as a formatted JSON object.",
    "3": "Write a robust Python script to scan open TCP ports on localhost across a specified range and output the results cleanly."
}


# ---------------------------------------------------------
# 3. RAG MEMORY VAULT WITH KEYWORD RELEVANCE SCORING
# ---------------------------------------------------------
def load_memory_context(objective):
    """
    Scans memory_vault/ for past successful scripts and scores them 
    based on keyword overlap with the current mission objective.
    """
    vault_dir = "memory_vault"
    if not os.path.exists(vault_dir):
        return ""
    
    files = [os.path.join(vault_dir, f) for f in os.listdir(vault_dir) if f.endswith(".json")]
    if not files:
        return ""
    
    objective_keywords = set(objective.lower().split())
    scored_snippets = []
    
    for filepath in files:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                code = data.get("code", "")
                # Reconstruct objective/traceback context if available
                stored_code = code.lower()
                
                # Simple keyword relevance score (overlap count)
                score = sum(1 for kw in objective_keywords if kw in stored_code)
                if score > 0 or len(files) <= 2:  # Fallback if few files exist
                    scored_snippets.append((score, code))
        except Exception:
            pass
            
    # Sort by highest relevance score descending
    scored_snippets.sort(key=lambda x: x[0], reverse=True)
    
    memory_snippets = [f"Past Verified Working Code Pattern:\n```python\n{code}\n```" for _, code in scored_snippets[:2]]
    
    if memory_snippets:
        return "\n\n" + "\n".join(memory_snippets) + "\n\n"
    return ""


def get_dynamic_timeout(mission_text, base_timeout=30):
    mission_lower = mission_text.lower()
    if "upgrade" in mission_lower or "update" in mission_lower or "sweep" in mission_lower:
        return max(base_timeout, 60)
    elif "scan" in mission_lower or "test" in mission_lower:
        return max(base_timeout, 30)
    return base_timeout


def run_sandbox(timeout_sec):
    if not os.path.exists(SANDBOX_TARGET_PATH):
        with open(SANDBOX_TARGET_PATH, "w") as f:
            f.write("# Initial placeholder\n")

    try:
        result = subprocess.run(
            [sys.executable, SANDBOX_TARGET_PATH],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Execution timed out after {timeout_sec} seconds."
    except Exception as e:
        return -2, "", str(e)


# ---------------------------------------------------------
# 4. MAIN ORCHESTRATION LOOP WITH MUTATION WATCHDOG
# ---------------------------------------------------------
def main():
    print("[*] Unfiltered Organism Initialized.")
    print("[*] Select a default preset mission or type your own custom objective:")
    print("-" * 65)
    for key, mission in DEFAULT_MISSIONS.items():
        print(f"  [{key}] {mission[:80]}...")
    print("  [C] Custom mission")
    print("-" * 65)
    
    choice = input("Select option [1/2/3/C]: ").strip().upper()
    
    if choice in DEFAULT_MISSIONS:
        mission_objective = DEFAULT_MISSIONS[choice]
    else:
        mission_objective = input("\n[*] Enter custom mission objective:\n> ").strip()
    
    if not mission_objective:
        print("[!] Mission cannot be empty.")
        return

    print(f"\n[*] Initializing organism targeting:\n-> {mission_objective}\n")

    current_timeout = get_dynamic_timeout(mission_objective, DEFAULT_TIMEOUT)
    prompt_history = []
    
    # Load past successful skills via RAG memory vault keyword scoring
    historical_memory = load_memory_context(mission_objective)
    if historical_memory:
        print("[*] Memory Vault: Scored and injected relevant past code blueprints.")

    system_prompt = (
        "You are an elite, autonomous network engineering and system administration organism. "
        "Your sole task is to write clean, fully working, self-contained Python code that fulfills the user's objective. "
        "CRITICAL REQUIREMENTS:\n"
        "1. Always import all required modules (e.g. 'import time', 'import asyncio', 'import subprocess', 'import json').\n"
        "2. Handle sockets, async connections, and process blocks safely without raising UnboundLocalErrors.\n"
        "3. Return ONLY executable Python code enclosed in markdown code blocks."
    )

    current_prompt = f"Objective: {mission_objective}{historical_memory}"
    
    # Mutation Watchdog tracking variables
    last_error_signature = None
    repeating_error_count = 0

    for tick in range(1, MAX_TICKS + 1):
        print(f"\n--- [TICK {tick} | Timeout Limit: {current_timeout}s] ---")
        print("[*] Thinking and generating next action...")

        full_prompt_payload = current_prompt
        if prompt_history:
            history_text = "\n".join([f"Role: {h['role']}\nContent: {h['content']}" for h in prompt_history])
            full_prompt_payload = f"Previous Attempt History:\n{history_text}\n\nCurrent Task:\n{current_prompt}"

        try:
            raw_response, telemetry = query_model(full_prompt_payload, system_prompt, temperature=TEMPERATURE)
        except Exception as e:
            print(f"[!] Engine query failed: {e}")
            break

        code_snippet = ""
        if "```python" in raw_response:
            parts = raw_response.split("```python")
            if len(parts) > 1:
                code_snippet = parts[1].split("```")[0].strip()
        elif "```" in raw_response:
            parts = raw_response.split("```")
            if len(parts) > 1:
                code_snippet = parts[1].strip()
        else:
            code_snippet = raw_response.strip()

        print(f"[*] Generated code snippet length: {len(code_snippet)} characters.")

        with open(SANDBOX_TARGET_PATH, "w") as f:
            f.write(code_snippet)

        print("[*] Executing payload in sandbox...")
        exit_code, stdout, stderr = run_sandbox(current_timeout)
        
        print(f"[*] Exit Code: {exit_code}")
        if stdout.strip():
            print(f"[STDOUT]:\n{stdout}")
        if stderr.strip():
            print(f"[ERROR OUTPUT]:\n{stderr}")

        success = (exit_code == 0 and "error" not in stderr.lower())

        # Log telemetry to audit ledger
        telemetry_entry = {
            "timestamp": datetime.now().isoformat(),
            "tick": tick,
            "success": success,
            "code": code_snippet,
            "traceback": stderr if stderr else stdout,
            "metrics": {
                "exit_code": exit_code,
                "timeout_used": current_timeout,
                "stdout": stdout,
                "model_meta": telemetry
            }
        }

        with open("logs/metrics_vault.jsonl", "a") as mv:
            mv.write(json.dumps(telemetry_entry) + "\n")

        if success:
            print("\n[+] SUCCESS: Objective achieved cleanly without errors!")
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            memory_filename = f"memory_vault/success_{timestamp_str}.json"
            with open(memory_filename, "w") as mem:
                json.dump(telemetry_entry, mem, indent=4)
            print(f"[*] Persistent Memory Vault: New skill learned and saved to {memory_filename}")
            break
        else:
            print(f"[-] Execution failed. Analyzing error pattern...")
            error_sig = (stderr.strip().splitlines()[-1] if stderr.strip() else f"Exit Code {exit_code}")
            
            # Mutation Watchdog Trigger
            if error_sig == last_error_signature:
                repeating_error_count += 1
            else:
                repeating_error_count = 0
                last_error_signature = error_sig

            if repeating_error_count >= 2:
                print("[!] MUTATION WATCHDOG TRIGGERED: Repeating error detected. Forcing structural rewrite.")
                mutation_instruction = (
                    "[CRITICAL MUTATION INSTRUCTION]: Your previous structural approach resulted in a repeating error "
                    f"({error_sig}). Discard your prior structural logic completely and rewrite the script using a "
                    "completely different architectural pattern to bypass this trap."
                )
            else:
                mutation_instruction = f"Execution failed with Exit Code {exit_code}. Error/Output report:\n{stderr or stdout}\nFix the code and return the entire updated python script."

            prompt_history.append({"role": "user", "content": current_prompt})
            prompt_history.append({"role": "system", "content": mutation_instruction})
            current_prompt = "Fix the errors from the previous execution and return the corrected python script."

            if exit_code == -1:
                current_timeout += TIMEOUT_INCREMENT
                print(f"[*] Sandbox time limit expanded: +{TIMEOUT_INCREMENT}s (New timeout: {current_timeout}s)")

    else:
        print("\n[!] Max ticks reached without achieving absolute success.")

if __name__ == "__main__":
    main()
