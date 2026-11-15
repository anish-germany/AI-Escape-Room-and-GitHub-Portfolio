"""Minimal Gemini REST adapter. No keys in URLs, logs or browser state."""
import os
import re
import requests


class LLMError(RuntimeError):
    pass


def generate(system, messages):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise LLMError("No API key configured. Add GEMINI_API_KEY to your local .env.")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if not re.fullmatch(r"[a-zA-Z0-9.-]+", model):
        raise LLMError("Invalid model name in GEMINI_MODEL.")
    contents = [{"role": "model" if m["role"] == "assistant" else "user",
                 "parts": [{"text": m["content"]}]} for m in messages]
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": key},
            json={"systemInstruction": {"parts": [{"text": system}]},
                  "contents": contents,
                  "generationConfig": {"temperature": 0.4, "maxOutputTokens": 700}},
            timeout=(5, 25),
        )
        if response.status_code != 200:
            raise LLMError(f"Gemini request failed (HTTP {response.status_code}). Check key, model and free quota.")
        data = response.json()
        result = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
        if not result.strip():
            raise LLMError("Gemini returned no text. Please try again.")
        return result.strip()
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        raise LLMError("Gemini is unavailable or returned an unsupported response. Please try again.") from None
