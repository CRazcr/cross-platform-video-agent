from __future__ import annotations

import json
import logging
from typing import Any

from .prompts import STRUCTURE_VALIDATION_PROMPT

logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass


REQUIRED_SCRIPT_FIELDS = ["title", "rhythm_text", "storyboard", "hashtags", "publish_time_suggestion"]


def parse_json_response(raw: str, max_retries: int = 2) -> dict[str, Any]:
    for attempt in range(max_retries + 1):
        try:
            cleaned = _extract_json(raw)
            data = json.loads(cleaned)
            if attempt == 0:
                return data
            logger.info("JSON解析重试成功 (第%d次)", attempt + 1)
            return data
        except (json.JSONDecodeError, ValueError) as e:
            if attempt < max_retries:
                logger.warning("JSON解析失败 (第%d次)，尝试LLM修复: %s", attempt + 1, e)
                raw = _llm_fix_json(raw)
            else:
                raise ParseError(f"JSON解析失败（已重试{max_retries}次）: {e}")


def _extract_json(text: str) -> str:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text


def _llm_fix_json(raw: str) -> str:
    from ..llm.client import get_llm_client

    client = get_llm_client()
    prompt = STRUCTURE_VALIDATION_PROMPT.format(raw_response=raw[:3000])
    try:
        result = client.chat_json(
            system_prompt="你是一个JSON修复专家。",
            user_prompt=prompt,
            temperature=0.1,
        )
        if result.get("valid") and result.get("fixed_json"):
            if isinstance(result["fixed_json"], dict):
                return json.dumps(result["fixed_json"], ensure_ascii=False)
            return json.dumps(result["fixed_json"])
        if not result.get("valid"):
            raise ValueError(f"JSON无法修复: {result.get('error', '未知错误')}")
        return raw
    except Exception:
        return raw


def validate_script_fields(data: dict[str, Any], platform_key: str) -> dict[str, Any]:
    if "script" not in data:
        data = {"script": data}
    script = data["script"]
    missing = [f for f in REQUIRED_SCRIPT_FIELDS if f not in script]
    if missing:
        logger.warning("平台 %s 脚本缺少字段: %s", platform_key, missing)
    if "title" not in script:
        script["title"] = "未生成标题"
    if "rhythm_text" not in script:
        script["rhythm_text"] = "未生成文案"
    if "storyboard" not in script:
        script["storyboard"] = []
    if "hashtags" not in script:
        script["hashtags"] = []
    if not isinstance(script.get("hashtags"), list):
        script["hashtags"] = [script["hashtags"]]
    if "publish_time_suggestion" not in script:
        script["publish_time_suggestion"] = ""
    return data