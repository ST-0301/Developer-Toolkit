import json
import requests

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

def test_ollama_connection():
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        response.raise_for_status()
        return True, "Connected successfully."
    except Exception as e:
        return False, str(e)

def summarize_chunk(model_name, chunk_text):
    """Uses the FAST model to rapidly extract bullet points."""
    chunk_prompt = f"""
You are a technical assistant processing a log file. 
Summarize the following chunk accurately in bullet points. 
Retain all technical details, metrics, problems, and names. 
Keep it extremely brief.

=== CHUNK DATA ===
{chunk_text}
"""
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": model_name,
            "prompt": chunk_prompt,
            "stream": False,
            "options": {
                "num_batch": 256,  
                "num_ctx": 4096,
                "num_predict": 300
            }
        },
        timeout=6000
    )
    response.raise_for_status()
    return response.json()["response"]

def generate_journal(model_name, prompt, context):
    """Uses the SMART model to generate the final journal."""
    full_prompt = f"""
{prompt}

=== CONTEXT DATA ===
{context}
"""
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_batch": 256,
                "num_ctx": 8192
            }
        },
        timeout=6000
    )
    response.raise_for_status()
    return response.json()["response"]

def translate_message(model_name, system_prompt, scenario, tone, raw_message):
    """
    Sends the raw message to Ollama, requesting a JSON response containing
    both the detected emotion and the rewritten message.
    """
    full_prompt = f"""{system_prompt}

=== CONTEXT ===
Scenario: {scenario}
Target Tone: {tone}

=== RAW MESSAGE ===
{raw_message}
"""
    
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "num_predict": 500,
                "temperature": 0.3
            }
        },
        timeout=6000
    )
    
    response.raise_for_status()
    result_text = response.json()["response"].strip()
    
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "detected_emotion": "Unknown", 
            "rewritten_message": result_text
        }