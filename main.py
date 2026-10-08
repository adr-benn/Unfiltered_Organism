import os
import sys
import json
import subprocess
import time
from datetime import datetime

# Configuration
SANDBOX_FILE = "sandbox_target.py"
VAULT_DIR = "memory_vault"
DEFAULT_TIMEOUT = 10
TIMEOUT_INCREMENT = 15
MAX_TICKS = 15

def retrieve_memory_context(user_prompt):
    """Scans the memory_vault/ directory for past successful scripts using keyword matching."""
    if not os.path.exists(VAULT_DIR):
        return ""
    
    prompt_words = set(user_prompt.lower().split())
    best_match_code = None
    highest_score = 0
    
    for filename in os.listdir(VAULT_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(VAULT_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    memory_data = json.load(f)
                    
                tags = set(memory_data.get("tags", []))
                score = len(prompt_words.intersection(tags))
                
                if score > highest_score:
                    highest_score = score
                    best_match_code = memory_data.get("code")
            except Exception:
                continue
                
    if best_match_code and highest_score > 0:
        print(f"[*] Memory Vault: Found relevant past solution (Relevance Score: {highest_score})")
        return f"\n\n[MEMORIZED REFERENCE BLUEPRINT]:\nHere is a script you successfully wrote previously for a similar objective. Study its error-free structure and use it as a base:\n```python\n{best_match_code}\n```\n"
    
    return ""

def save_to_memory_vault(objective, code_content):
    """Automatically saves a successful script into a new JSON file in the memory vault."""
    os.makedirs(VAULT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"memory_vault/success_{timestamp}.json"
    
    # Extract simple tags from objective
    words = [w.strip('.,/?!()') for w in objective.lower().split()]
    common_tags = [w for w in words if len(w) > 3][:8] # grab key words
    
    memory_payload = {
        "id": f"success_{timestamp}",
        "objective": objective,
        "tags": common_tags,
        "code": code_content
    }
    
    try:
        with open(filename, "w") as f:
            json.dump(memory_payload, f, indent=4)
        print(f"[*] Persistent Memory Vault: New skill learned and saved to {filename}")
    except Exception as e:
        print(f"[!] Warning: Failed to save to memory vault: {e}")

def query_ollama(prompt_history):
    """Sends prompt history to local Ollama instance running qwen2.5-coder:7b."""
    import urllib.request
    
    url = "http://localhost:11434/api/generate"
    full_prompt = "\n".join([item['content'] for item in prompt_history])
    
    data = {
        "model": "qwen2.5-coder:7b",
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            return res_body.get("response", "")
    except Exception as e:
        print(f"[!] Error communicating with Ollama: {e}")
        return ""

def extract_python_code(text):
    """Extracts raw Python code blocks from markdown formatting if present."""
    if "```python" in text:
        parts = text.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")[0]
            return code.strip()
    elif "```" in text:
        parts = text.split("```")
        if len(parts) > 1:
            code = parts[1].split("```")[0]
            return code.strip()
    return text.strip()

def run_sandbox(timeout_sec):
    """Executes the generated sandbox script and returns exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            [sys.executable, SANDBOX_FILE],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Execution timed out after {timeout_sec} seconds."
    except Exception as e:
        return -1, "", str(e)

def main():
    print("[*] What is the mission for the organism today? (Press Enter to use default async scanner):")
    user_input = input("> ").strip()
    
    default_mission = (
        "Write an advanced asynchronous Python script using 'asyncio' and 'socket' "
        "that performs a high-speed network sweep across a local subnet range (e.g., 192.168.1.1 to 192.168.1.50) "
        "for core management ports (22, 80, 443, 8006). The script must use an asyncio.Semaphore(30) "
        "to limit concurrency, measure RTT in milliseconds with time.perf_counter(), "
        "and output the results as a validated JSON array."
    )
    
    mission = user_input if user_input else default_mission
    print(f"\n[*] Initializing Unfiltered Organism targeting:\n-> {mission}\n")
    
    # Check RAG memory vault for prior blueprints
    memory_injection = retrieve_memory_context(mission)
    
    system_prompt = (
        "You are an elite, autonomous network engineering organism. Your sole task is to write "
        "clean, fully working, self-contained Python code that fulfills the user's objective. "
        "Return ONLY executable Python code enclosed in markdown code blocks. "
        "Do not include conversational filler text."
    )
    
    prompt_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Objective: {mission}{memory_injection}"}
    ]
    
    current_timeout = DEFAULT_TIMEOUT
    last_error_signature = None
    loop_count = 0
    
    for tick in range(1, MAX_TICKS + 1):
        print(f"\n--- [TICK {tick} | Timeout Limit: {current_timeout}s] ---")
        print("[*] Thinking and generating next action...")
        
        raw_response = query_ollama(prompt_history)
        clean_code = extract_python_code(raw_response)
        
        print(f"[*] Generated code snippet length: {len(clean_code)} characters.")
        
        with open(SANDBOX_FILE, "w") as f:
            f.write(clean_code)
            
        print(f"[*] Executing payload in sandbox (max {current_timeout}s)...")
        exit_code, stdout, stderr = run_sandbox(current_timeout)
        
        print(f"[*] Exit Code: {exit_code}")
        
        if exit_code == 0:
            if stdout.strip():
                print(f"[STDOUT]:\n{stdout}")
            print("\n[+] SUCCESS: Objective achieved cleanly without errors!")
            
            # Automatically commit to the JSON memory vault
            save_to_memory_vault(mission, clean_code)
            break
            
        # Error handling & loop detection
        error_output = stderr if stderr else stdout
        print(f"[STDERR - ERROR]:\n{error_output}")
        
        # Check if identical error signature is looping
        if error_output == last_error_signature:
            loop_count += 1
        else:
            loop_count = 0
            last_error_signature = error_output
            
        if loop_count >= 2:
            print("[!] LOOP DETECTED: Organism is repeating the exact same error signature. Forcing architectural mutation.")
            mutation_prompt = (
                f"[CRITICAL MUTATION INSTRUCTION]: Your previous approach resulted in a repeating error. "
                f"Discard your prior structural logic completely. Here is the persistent error traceback:\n{error_output}\n"
                "Rewrite the entire script using a completely different architectural pattern to bypass this trap."
            )
            prompt_history.append({"role": "user", "content": mutation_prompt})
            loop_count = 0
        else:
            feedback_prompt = (
                f"Your execution failed with Exit Code {exit_code}. Here is the traceback/error output:\n"
                f"{error_output}\n\nFix the code and return the entire updated python script."
            )
            prompt_history.append({"role": "user", "content": feedback_prompt})
            
        # Dynamically scale timeout if it timed out
        if exit_code == -1 and "timed out" in error_output.lower():
            current_timeout += TIMEOUT_INCREMENT
            print(f"[*] Sandbox time limit expanded. New timeout: {current_timeout}s")

if __name__ == "__main__":
    main()
