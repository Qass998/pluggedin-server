#!/usr/bin/env python3
"""
OpenRouter status and helper CLI for PluggedIN.

Usage:
  python openrouter_status.py status
  python openrouter_status.py list
  python openrouter_status.py test --task scoring
  python openrouter_status.py test --model qwen/qwen3.6-flash --prompt "Write a haiku"
"""

import argparse
import os
import requests
from dotenv import load_dotenv

from lib.ai_client import get_task_model_map, OPENROUTER_DEFAULT_MODEL, OPENROUTER_API_KEY, OPENROUTER_BASE

load_dotenv()

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


def print_status():
    print("OpenRouter status")
    print("-------------------")
    print(f"OPENROUTER_API_KEY: {'SET' if OPENROUTER_API_KEY else 'NOT SET'}")
    print(f"OPENROUTER_DEFAULT_MODEL: {OPENROUTER_DEFAULT_MODEL or 'None'}")
    print("\nTask → model mapping:")
    for task, model in get_task_model_map().items():
        print(f"  {task}: {model}")


def list_models():
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in .env")

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    resp = requests.get(OPENROUTER_MODELS_URL, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    print(f"Found {len(data)} OpenRouter models")
    for model in data[:100]:
        print(f"- {model.get('id')}")


def test_model(model: str, prompt: str):
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in .env")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 200,
    }

    resp = requests.post(OPENROUTER_BASE, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    print(f"\nModel: {model}\nResponse:\n{text}\n")


def main():
    parser = argparse.ArgumentParser(description="OpenRouter helper for PluggedIN")
    parser.add_argument("command", choices=["status", "list", "test"], help="Command to run")
    parser.add_argument("--task", help="Task name to test from ai_client model map")
    parser.add_argument("--model", help="OpenRouter model name to test directly")
    parser.add_argument("--prompt", default="Write a short friendly summary of OpenRouter.", help="Prompt for model testing")
    args = parser.parse_args()

    if args.command == "status":
        print_status()
    elif args.command == "list":
        list_models()
    elif args.command == "test":
        if args.model:
            model = args.model
        elif args.task:
            task_map = get_task_model_map()
            model = task_map.get(args.task)
            if not model:
                raise ValueError(f"Unknown task: {args.task}")
        else:
            raise ValueError("Provide --task or --model for test")
        test_model(model=model, prompt=args.prompt)


if __name__ == "__main__":
    main()
