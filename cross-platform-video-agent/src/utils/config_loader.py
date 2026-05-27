from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def load_json_config(filename: str) -> dict[str, Any]:
    filepath = _CONFIG_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"配置文件不存在: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_platform_rules() -> dict[str, Any]:
    return load_json_config("platform_rules.json")


def load_llm_config() -> dict[str, Any]:
    return load_json_config("llm_config.json")


def load_feishu_config() -> dict[str, Any]:
    return load_json_config("feishu_config.json")