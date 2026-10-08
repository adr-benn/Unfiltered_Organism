"""
engine.py - The LLM Communication Layer
---------------------------------------
 guía del desarrollador (Developer Guide):
 This file abstracts the LLM backend from the main controller loop.
 
 HOW TO SWITCH MODELS:
 - Local Ollama: Change MODEL_NAME to any pulled model (e.g., 'llama3.1:8b', 'gemma2:2b')
 - Cloud APIs (OpenAI/Anthropic/Gemini): Swap out requests.post() logic here 
   to point to your cloud endpoint with an authorization header.
"""

import requests
import json
import os

# Configuration variables (overridable via environment variables)
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5-coder:7b")
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:11434/api/generate")

def query_model(prompt_text, system_prompt=""):
    """
    Sends the compiled prompt history to the configured local or cloud LLM 
    and returns the raw text response alongside telemetry token metrics.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\n{prompt_text}",
        "stream": False,
        "options": {
            "temperature": 0.2  # Low temperature ensures deterministic code syntax
        }
    }

    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            generated_response = data.get("response", "")
            eval_count = data.get("eval_count", 0)  # Token generation count
            return generated_response, {"eval_count": eval_count}
        else:
            raise RuntimeError(f"Engine responded with status {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to LLM engine at {API_ENDPOINT}: {e}")
