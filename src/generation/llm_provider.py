import os
import httpx
from abc import ABC, abstractmethod
from openai import OpenAI
from anthropic import Anthropic

from config.settings import settings


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, model: str = settings.LLM_MODEL, api_key: str | None = settings.OPENAI_API_KEY):
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            return "Error: OpenAI API key missing."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""


class AnthropicLLMProvider(BaseLLMProvider):
    def __init__(self, model: str = "claude-3-haiku-20240307", api_key: str | None = settings.ANTHROPIC_API_KEY):
        self.model = model
        self.client = Anthropic(api_key=api_key) if api_key else None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            return "Error: Anthropic API key missing."
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.2,
        )
        block = response.content[0]
        text = block.text if hasattr(block, "text") else str(block)
        return text.strip() if text else ""


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        self.model = model if "gemini" in model else "gemini-2.5-flash"
        key = api_key or getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
        self.api_key = key.strip() if key else None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key or "YOUR_" in self.api_key:
            return "Error: Gemini API key missing."
        
        # Priority order of available Gemini models
        model_candidates = [
            self.model.replace("models/", ""),
            "gemini-2.5-flash",
            "gemini-3.6-flash",
            "gemini-2.5-pro",
            "gemini-2.5-flash-lite",
            "gemini-flash-latest"
        ]

        # Deduplicate candidates
        candidates = []
        for m in model_candidates:
            if m not in candidates:
                candidates.append(m)

        for model_name in candidates:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}]
            }
            try:
                resp = httpx.post(url, json=payload, timeout=25.0)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates_res = data.get("candidates", [])
                    if candidates_res and "content" in candidates_res[0]:
                        parts = candidates_res[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
            except Exception:
                continue

        return "Error: All Gemini model attempts returned non-200 responses."



def get_llm_provider(provider_name: str = settings.LLM_PROVIDER) -> BaseLLMProvider:
    p = provider_name.lower()
    if p == "openai":
        return OpenAILLMProvider()
    elif p == "anthropic":
        return AnthropicLLMProvider()
    elif p == "gemini":
        return GeminiLLMProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
