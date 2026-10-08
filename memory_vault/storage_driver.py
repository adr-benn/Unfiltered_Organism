"""
memory_vault/storage_driver.py - Pluggable Persistence & Telemetry Layer
------------------------------------------------------------------------
 DEVELOPER EXTENSION GUIDE:
 Currently configured to log execution metrics and tracebacks to line-delimited 
 JSON files (metrics_vault.jsonl) inside the logs/ directory.
 
 TO UPGRADE TO SQLITE / POSTGRESQL:
 - You can rewrite the methods below to open an SQL connection instead of writing 
   to flat files. 
 - Because main.py only calls StorageDriver.log_execution(), swapping your backend 
   here requires ZERO modifications to the rest of the codebase.
"""

import json
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class StorageDriver:
    @staticmethod
    def log_execution(tick, code_generated, success, traceback=None, metrics=None):
        """
        Appends structured execution telemetry, source code snapshots, 
        and error tracebacks to the metrics ledger.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tick": tick,
            "success": success,
            "code": code_generated,
            "traceback": traceback,
            "metrics": metrics or {}
        }

        metrics_file = os.path.join(LOG_DIR, "metrics_vault.jsonl")
        try:
            with open(metrics_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[!] Storage Driver Warning: Failed to write metric entry: {e}")
