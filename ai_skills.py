"""
ai_skills.py — AI helpers using Groq REST API
"""

import json
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()  # loads .env file automatically

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama-3.1-8b-instant"


def _ask(prompt: str, max_tokens: int = 600) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file: GROQ_API_KEY=your_key_here"
        )
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    if r.status_code == 401:
        raise RuntimeError("Groq API key is invalid or expired. Get a new one at console.groq.com")
    if r.status_code == 429:
        raise RuntimeError("Groq API rate limit hit. Wait a moment and try again.")
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def generate_job_skills(job_role: str) -> dict:
    prompt = f"""List the specific skills required for a "{job_role}" position in 2025.

Return ONLY this JSON, no other text:
{{
  "technical": ["skill1", "skill2"],
  "soft": ["skill1", "skill2"]
}}

For "{job_role}", the technical skills must be SPECIFIC to this exact role only.
- technical: exactly 10 skills, all lowercase, ONLY skills directly used in this specific job
- soft: exactly 6 skills, all lowercase
- NO generic programming skills unless they are core to THIS specific role
- JSON only, no explanation"""
    for attempt in range(3):
        try:
            raw = _ask(prompt)
            raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"\n?```$", "", raw, flags=re.IGNORECASE)
            data = json.loads(raw.strip())
            technical = [s.strip().lower() for s in data.get("technical", []) if s.strip()]
            soft      = [s.strip().lower() for s in data.get("soft", []) if s.strip()]
            if len(technical) < 3:
                raise ValueError("Too few skills")
            return {"technical": technical, "soft": soft}
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == 2:
                raise ValueError(f"Failed to generate skills for '{job_role}'")
    return {"technical": [], "soft": []}


def suggest_skills(user_skills: list, target_job: str) -> list:
    prompt = f"""I want to become a {target_job}.
I already know: {', '.join(user_skills) if user_skills else 'none'}.
Suggest 8 skills to learn next.
Give only comma-separated skill names, nothing else."""
    try:
        text = _ask(prompt, max_tokens=200)
        return [s.strip() for s in text.split(",") if s.strip()]
    except Exception as e:
        print("suggest_skills error:", e)
        return ["AI failed to fetch skill suggestions"]