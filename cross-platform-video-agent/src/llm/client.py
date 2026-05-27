from __future__ import annotations

import json
from typing import Any

import requests

from ..utils.config_loader import load_llm_config


class LLMClient:
    def __init__(self, config: dict[str, Any] | None = None):
        if config is None:
            config = load_llm_config()
        self.config = config
        self.api_base = config.get("api_base", "https://api.deepseek.com/v1").rstrip("/")
        self.api_key = config["api_key"]
        self.model = config.get("model", "deepseek-chat")
        self.default_temperature = config.get("temperature", 0.8)
        self.default_max_tokens = config.get("max_tokens", 4096)
        self.max_retries = config.get("max_retries", 3)
        self.request_timeout = config.get("request_timeout", 60)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict[str, str] | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.default_max_tokens,
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                resp = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                    timeout=self.request_timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                if content is None:
                    raise ValueError("LLM 返回了空内容")
                return content
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    continue

        raise RuntimeError(
            f"LLM 调用失败（已重试 {self.max_retries} 次），最后错误: {last_error}"
        )

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.default_max_tokens,
            "response_format": {"type": "json_object"},
        }

        resp = requests.post(
            f"{self.api_base}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=self.request_timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)


_llm_client_instance: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient()
    return _llm_client_instance
