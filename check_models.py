"""
Check available OpenRouter models
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Fetch available models
url = "https://openrouter.ai/api/v1/models"
headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}

response = requests.get(url, headers=headers)
data = response.json()

print("Available OpenRouter Models:\n")
for model in data.get("data", [])[:20]:  # Show first 20
    print(f"✓ {model['id']}")
