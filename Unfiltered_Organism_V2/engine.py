import os
import requests

MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5-coder:14b-instruct-q4_K_M")

def query_model(prompt, system_prompt="", temperature=0.2):
    """
    Universal engine routing requests, supporting configurable temperature.
    """
    eval_count = 0

    # 1. ANTHROPIC CLAUDE ROUTE
    if "claude" in MODEL_NAME.lower():
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2048,
            system=system_prompt if system_prompt else None,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        text = response.content[0].text
        if response.usage:
            eval_count = response.usage.output_tokens
            
    # 2. GOOGLE GEMINI ROUTE
    elif "gemini" in MODEL_NAME.lower():
        from google import genai
        from google.genai import types
        client = genai.Client()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )
        text = response.text
        if response.usage_metadata:
            eval_count = response.usage_metadata.candidates_token_count
            
    # 3. OPENAI GPT ROUTE
    elif "gpt" in MODEL_NAME.lower() or "o3" in MODEL_NAME.lower():
        from openai import OpenAI
        client = OpenAI()
        messages = []
        if system_prompt:
            messages.append({"role": "developer", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        text = response.choices[0].message.content
        if response.usage:
            eval_count = response.usage.completion_tokens
            
    # 4. LOCAL OLLAMA ROUTE (Default)
    else:
        api_endpoint = "http://localhost:11434/api/generate"
        full_prompt = f"System Instruction: {system_prompt}\n\nUser Objective: {prompt}" if system_prompt else prompt
        
        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }
        
        response = requests.post(api_endpoint, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        text = data.get("response", "")
        eval_count = data.get("eval_count", 0)

    telemetry = {
        "eval_count": eval_count,
        "model": MODEL_NAME,
        "temperature": temperature
    }
    
    return text, telemetry
