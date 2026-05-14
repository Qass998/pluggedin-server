"""
OpenRouter Client — Backup AI Models for Free/Cheap Inference
Free: google/gemma-4
Cheap: deepseek/deepseek-r2, moonshot/kimi-2.5
"""

import os
import json
from dotenv import load_dotenv
import openai

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model shortcuts
MODELS = {
    "gemma": "poolside/laguna-xs.2:free",           # Free — research & monitoring
    "deepseek": "qwen/qwen3.5-plus-20260420",  # Fast — coding backup
    "kimi": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",         # Reasoning
    "llama": "qwen/qwen3.6-flash",       # General purpose
}


class OpenRouterClient:
    """
    Unified OpenRouter client for all models.
    Auto-routes to cheapest model if cost matters.
    """

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set in .env")
        
        self.client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )

    def chat(self, messages: list, model: str = "gemma", temperature: float = 0.7, max_tokens: int = 2000):
        """
        Send a chat request to OpenRouter.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model shortcut (gemma, deepseek, kimi, llama)
            temperature: 0.0-2.0, higher = more creative
            max_tokens: Max output tokens
            
        Returns:
            Generated text
        """
        model_id = MODELS.get(model, model)
        
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter error: {e}")
            raise

    def research(self, topic: str) -> str:
        """Quick research task using free Gemma model."""
        messages = [{"role": "user", "content": f"Research and summarize: {topic}"}]
        return self.chat(messages, model="gemma", max_tokens=1500)

    def code(self, prompt: str) -> str:
        """Generate code using DeepSeek (cheap, fast)."""
        messages = [{"role": "user", "content": f"Generate code:\n{prompt}"}]
        return self.chat(messages, model="deepseek", max_tokens=3000)

    def reason(self, prompt: str) -> str:
        """Complex reasoning using Kimi."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model="kimi", temperature=0.3, max_tokens=2000)

    def monitor(self, prompt: str) -> str:
        """Monitoring task — ultra cheap, Gemma free tier."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model="gemma", max_tokens=1000)


# Singleton instance
_client = None

def get_client():
    """Get or create the OpenRouter client."""
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client


# Quick access functions
def research(topic: str) -> str:
    """Quick research using free Gemma model."""
    return get_client().research(topic)


def code(prompt: str) -> str:
    """Generate code using cheap DeepSeek model."""
    return get_client().code(prompt)


def reason(prompt: str) -> str:
    """Complex reasoning using Kimi."""
    return get_client().reason(prompt)


def monitor(prompt: str) -> str:
    """Ultra-cheap monitoring."""
    return get_client().monitor(prompt)


if __name__ == "__main__":
    # Test connection
    client = get_client()
    print("✓ OpenRouter connected")
    
    # Test quick research
    print("\n[Gemma Test]")
    result = research("What is PluggedIN?")
    print(result[:200] + "...")
