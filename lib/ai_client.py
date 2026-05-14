"""
ai_client.py — PluggedIN Shared AI Client
Single source of truth for all AI model calls across the system.
Routes via OpenRouter with automatic fallback.
All lib/ files import call_ai() from here — never call Anthropic directly.

Usage:
    from lib.ai_client import call_ai
    result = call_ai("scoring", system="...", prompt="...")
    result = call_ai("knowledge", system="...", prompt="...", max_tokens=2000)
"""

import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY      = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY       = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_DEFAULT_MODEL")
OPENROUTER_BASE          = "https://openrouter.ai/api/v1/chat/completions"

# ─────────────────────────────────────────────
# MODEL ROUTING TABLE
# Change models here — affects the entire system
# ─────────────────────────────────────────────

MODELS = {
    # Strategic / judgment tasks
    "chief":         "anthropic/claude-sonnet-4-6",
    "broker":        "anthropic/claude-sonnet-4-6",
    "ceo":           "anthropic/claude-haiku-4-5",
    "outreach":      "anthropic/claude-haiku-4-5",

    # Bulk reading / large context (Kimi = 1M token window, very cheap)
    "knowledge":     "moonshotai/kimi-k2",
    "market_intel":  "moonshotai/kimi-k2",
    "competitor":    "moonshotai/kimi-k2",
    "product_brief": "moonshotai/kimi-k2",

    # Fast data tasks
    "scoring":       "anthropic/claude-haiku-4-5",
    "logging":       "anthropic/claude-haiku-4-5",
    "opportunity":   "anthropic/claude-haiku-4-5",
}

# Tried in order if primary model fails
FALLBACK_CHAIN = [
    "anthropic/claude-haiku-4-5",
    "moonshotai/kimi-k2",
    "openai/gpt-4o-mini",
]


def call_ai(
    task: str,
    system: str,
    prompt: str,
    max_tokens: int = 1500,
    model_override: str = None,
) -> str:
    """
    Call an AI model via OpenRouter with automatic fallback.

    Args:
        task:           Key from MODELS dict — determines which model to use
        system:         System prompt
        prompt:         User prompt
        max_tokens:     Max tokens in response
        model_override: Force a specific model (OpenRouter format)

    Returns:
        str: Model response text

    Raises:
        RuntimeError: If all models and fallbacks fail
    """
    primary = model_override or OPENROUTER_DEFAULT_MODEL or MODELS.get(task, MODELS["scoring"])
    api_key = OPENROUTER_API_KEY or ANTHROPIC_API_KEY

    if not api_key:
        raise ValueError("No API key. Set OPENROUTER_API_KEY in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://pluggedin.ai",
        "X-Title":       "PluggedIN OS",
    }

    models_to_try = [primary] + [m for m in FALLBACK_CHAIN if m != primary]

    for attempt, model in enumerate(models_to_try):
        try:
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt},
                ],
            }

            resp = requests.post(OPENROUTER_BASE, headers=headers, json=payload, timeout=60)

            if resp.ok:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                if attempt > 0:
                    print(f"[ai_client] Fallback used: {model} (primary {primary} failed)")
                return text

            if resp.status_code == 429:
                print(f"[ai_client] Rate limited on {model}, retrying in 10s...")
                time.sleep(10)
                resp2 = requests.post(OPENROUTER_BASE, headers=headers, json=payload, timeout=60)
                if resp2.ok:
                    return resp2.json()["choices"][0]["message"]["content"].strip()

            print(f"[ai_client] {model} → {resp.status_code}, trying next...")

        except Exception as e:
            print(f"[ai_client] {model} error: {e}, trying next...")
            continue

    raise RuntimeError(f"All models failed for task '{task}'. Check OPENROUTER_API_KEY in .env")


def get_model_for_task(task: str) -> str:
    """Return the model name that will be used for a given task."""
    return OPENROUTER_DEFAULT_MODEL or MODELS.get(task, MODELS["scoring"])


def get_task_model_map() -> dict:
    """Return the current task-to-model mapping, including the default override."""
    result = dict(MODELS)
    if OPENROUTER_DEFAULT_MODEL:
        result["default_override"] = OPENROUTER_DEFAULT_MODEL
    return result
