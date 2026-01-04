from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from django.conf import settings

from crawler.models import CrawlerConfig


@dataclass(frozen=True)
class LLMResult:
    next_urls: List[str]
    next_urls_by_seed: List[Dict[str, str]]
    articles: List[Dict[str, Any]]


class LLMClient:
    def __init__(self, config: CrawlerConfig):
        self._config = config
        self._provider = (config.llm_provider or "openai").lower()
        self._api_key = config.llm_api_key or ""
        self._base_url = config.llm_base_url or self._default_base_url(self._provider)

    @staticmethod
    def _default_base_url(provider: str) -> str:
        if provider == "huggingface":
            return "https://api-inference.huggingface.co"
        if provider == "apifreellm":
            return "https://apifreellm.com"
        if provider in {"google", "gemini", "google_ai", "ai_studio"}:
            return "https://generativelanguage.googleapis.com/v1beta"
        return "https://api.openai.com/v1"

    @property
    def enabled(self) -> bool:
        if not self._config.llm_enabled:
            return False
        if self._provider == "apifreellm":
            return True
        if self._provider in {"google", "gemini", "google_ai", "ai_studio"}:
            return bool(self._api_key)
        return bool(self._api_key)

    def extract(self, prompt: str) -> Optional[LLMResult]:
        if not self.enabled:
            return None
        if self._provider == "huggingface":
            return self._extract_huggingface(prompt)
        if self._provider == "apifreellm":
            return self._extract_apifreellm(prompt)
        if self._provider in {"google", "gemini", "google_ai", "ai_studio"}:
            return self._extract_google(prompt)
        return self._extract_openai(prompt)

    def _extract_openai(self, prompt: str) -> Optional[LLMResult]:
        payload = {
            "model": self._config.llm_model,
            "temperature": self._config.llm_temperature,
            "max_tokens": self._config.llm_max_output_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a high-precision news extraction and URL selection system. "
                        "Only return valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=getattr(settings, "CRAWLER_LLM_TIMEOUT_SECONDS", 45)) as client:
                resp = client.post(
                    f"{self._base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            if resp.status_code >= 400:
                return None
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_response(content)
        except Exception:
            return None

    def _extract_huggingface(self, prompt: str) -> Optional[LLMResult]:
        payload = {
            "inputs": self._build_hf_prompt(prompt),
            "parameters": {
                "temperature": self._config.llm_temperature,
                "max_new_tokens": self._config.llm_max_output_tokens,
                "return_full_text": False,
            },
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=getattr(settings, "CRAWLER_LLM_TIMEOUT_SECONDS", 45)) as client:
                resp = client.post(
                    f"{self._base_url.rstrip('/')}/models/{self._config.llm_model}",
                    headers=headers,
                    json=payload,
                )
            if resp.status_code >= 400:
                return None
            data = resp.json()
            content = self._extract_hf_text(data)
            if not content:
                return None
            return self._parse_response(content)
        except Exception:
            return None

    def _extract_apifreellm(self, prompt: str) -> Optional[LLMResult]:
        payload = {"message": prompt}
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        try:
            with httpx.Client(timeout=getattr(settings, "CRAWLER_LLM_TIMEOUT_SECONDS", 45)) as client:
                resp = client.post(
                    f"{self._base_url.rstrip('/')}/api/chat",
                    headers=headers,
                    json=payload,
                )
            if resp.status_code >= 400:
                return None
            data = resp.json()
            content = self._extract_apifreellm_text(data)
            if not content:
                return None
            return self._parse_response(content)
        except Exception:
            return None

    def _extract_google(self, prompt: str) -> Optional[LLMResult]:
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": self._config.llm_temperature,
                "maxOutputTokens": self._config.llm_max_output_tokens,
            },
        }
        headers = {
            "x-goog-api-key": self._api_key,
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=getattr(settings, "CRAWLER_LLM_TIMEOUT_SECONDS", 45)) as client:
                resp = client.post(
                    f"{self._base_url.rstrip('/')}/models/{self._config.llm_model}:generateContent",
                    headers=headers,
                    json=payload,
                )
            if resp.status_code >= 400:
                return None
            data = resp.json()
            content = self._extract_google_text(data)
            if not content:
                return None
            return self._parse_response(content)
        except Exception:
            return None

    def _build_hf_prompt(self, prompt: str) -> str:
        return "Return ONLY valid JSON.\n" + prompt

    def _extract_hf_text(self, data: Any) -> Optional[str]:
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                return first.get("generated_text")
        if isinstance(data, dict):
            if "generated_text" in data:
                return data.get("generated_text")
            if "error" in data:
                return None
        return None

    def _extract_apifreellm_text(self, data: Any) -> Optional[str]:
        if isinstance(data, dict):
            for key in ("response", "message", "content", "text"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        return None

    def _extract_google_text(self, data: Any) -> Optional[str]:
        if not isinstance(data, dict):
            return None
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return None
        content = candidates[0].get("content")
        if not isinstance(content, dict):
            return None
        parts = content.get("parts")
        if not isinstance(parts, list):
            return None
        texts: List[str] = []
        for part in parts:
            if isinstance(part, dict):
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    texts.append(text)
        if not texts:
            return None
        return "\n".join(texts)

    def _parse_response(self, content: str) -> Optional[LLMResult]:
        try:
            data = json.loads(content)
        except Exception:
            return None
        if not isinstance(data, dict):
            return None
        next_urls = data.get("next_urls", [])
        next_urls_by_seed = data.get("next_urls_by_seed", [])
        articles = data.get("articles", [])
        if isinstance(next_urls_by_seed, dict):
            next_urls_by_seed = [
                {"seed_url": seed_url, "next_url": next_url}
                for seed_url, next_url in next_urls_by_seed.items()
            ]
        if (
            not isinstance(next_urls, list)
            or not isinstance(next_urls_by_seed, list)
            or not isinstance(articles, list)
        ):
            return None
        next_urls = [u for u in next_urls if isinstance(u, str)]
        next_urls_by_seed = [
            item for item in next_urls_by_seed if isinstance(item, dict)
        ]
        articles = [a for a in articles if isinstance(a, dict)]
        return LLMResult(
            next_urls=next_urls,
            next_urls_by_seed=next_urls_by_seed,
            articles=articles,
        )
