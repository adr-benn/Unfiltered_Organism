"""
memory_vault/storage_driver.py - Pluggable Persistence & Telemetry Layer
------------------------------------------------------------------------
 DEVELOPER EXTENSION GUIDE:
 Handles all file I/O, execution metrics, chat history logging, and memory vault 
 persistence. Designed with database-agnostic abstractions so you can swap 
 JSON flat files for an SQL connection in the future with zero modifications to main.py.
"""

import json
import os
from datetime import datetime

class StorageDriver:
    LOG_DIR = "logs"
    VAULT_DIR = "memory_vault"

    @classmethod
    def initialize_storage(cls):
        """Ensures required directories exist."""
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.VAULT_DIR, exist_ok=True)

    @classmethod
    def log_execution(cls, tick, code_generated, success, traceback=None, metrics=None):
        """Appends structured execution telemetry and conversation history to the logs ledger."""
        cls.initialize_storage()
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tick": tick,
            "success": success,
            "code": code_generated,
            "traceback": traceback,
            "metrics": metrics or {}
        }

        metrics_file = os.path.join(cls.LOG_DIR, "metrics_vault.jsonl")
        try:
            with open(metrics_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[!] Storage Driver Warning: Failed to write metric entry: {e}")

    @classmethod
    def save_memory_blueprint(cls, objective, code_content):
        """Saves a successful script into the memory vault as a reusable skill."""
        cls.initialize_storage()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(cls.VAULT_DIR, f"success_{timestamp}.json")
        
        words = [w.strip('.,/?!()') for w in objective.lower().split()]
        common_tags = [w for w in words if len(w) > 3][:8]
        
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
            print(f"[!] Warning: Failed to save memory blueprint: {e}")

    @classmethod
    def retrieve_memory_context(cls, user_prompt):
        """Scans the memory vault for past successful scripts using keyword matching."""
        cls.initialize_storage()
        if not os.path.exists(cls.VAULT_DIR):
            return ""
        
        prompt_words = set(user_prompt.lower().split())
        best_match_code = None
        highest_score = 0
        
        for filename in os.listdir(cls.VAULT_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(cls.VAULT_DIR, filename)
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
