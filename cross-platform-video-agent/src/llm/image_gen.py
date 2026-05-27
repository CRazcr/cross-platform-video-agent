from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

import requests

from ..utils.config_loader import load_llm_config


class ImageGenClient:
    def __init__(self, config: dict[str, Any] | None = None):
        if config is None:
            config = load_llm_config()
        self.config = config
        self.api_base = config.get("api_base", "https://api.deepseek.com/v1").rstrip("/")
        self.api_key = config["api_key"]
        self.model = config.get("image_model", "dall-e-3")
        self.size = config.get("image_size", "1024x1024")
        self.quality = config.get("image_quality", "standard")
        self.request_timeout = config.get("request_timeout", 120)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate_cover(self, script_title: str, content_theme: str, style: str = "电影感") -> str:
        prompt = (
            f"Create a cinematic, professional video thumbnail for a short video. "
            f"Theme: {content_theme}. Title: {script_title}. "
            f"Style: {style}, high contrast, vivid colors, vertical 9:16 aspect ratio friendly composition. "
            f"Text on image: '{script_title}' in bold Chinese typography. "
            f"No Watermark. Professional color grading."
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": self.size,
            "quality": self.quality,
            "n": 1,
            "response_format": "b64_json",
        }

        resp = requests.post(
            f"{self.api_base}/images/generations",
            headers=self._headers(),
            json=payload,
            timeout=self.request_timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["b64_json"]

    def generate_scene_image(
        self, scene_description: str, platform: str, index: int
    ) -> str:
        style_map = {
            "douyin": "bold colors, dynamic angles, social media trending style",
            "shipinhao": "warm, authentic, documentary feel, WeChat ecosystem style",
            "bilibili": "anime-influenced, slightly stylized, otaku culture aesthetic",
        }
        style = style_map.get(platform, "cinematic")

        prompt = (
            f"A film storyboard scene illustration. "
            f"Scene {index}: {scene_description}. "
            f"Style: {style}. "
            f"Vertical 9:16 composition, high visual impact. "
            f"No text. No watermark."
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": "1024x1792",
            "quality": self.quality,
            "n": 1,
            "response_format": "b64_json",
        }

        resp = requests.post(
            f"{self.api_base}/images/generations",
            headers=self._headers(),
            json=payload,
            timeout=self.request_timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["b64_json"]

    @staticmethod
    def b64_to_bytes(b64: str) -> bytes:
        return base64.b64decode(b64)

    @staticmethod
    def save_b64_image(b64: str, filepath: str | Path) -> Path:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(base64.b64decode(b64))
        return filepath


_image_gen_client: ImageGenClient | None = None


def get_image_gen_client() -> ImageGenClient:
    global _image_gen_client
    if _image_gen_client is None:
        _image_gen_client = ImageGenClient()
    return _image_gen_client
