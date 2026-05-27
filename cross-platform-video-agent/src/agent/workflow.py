from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from ..llm.client import get_llm_client
from ..llm.image_gen import get_image_gen_client
from ..platforms.base import PlatformRule
from ..platforms.douyin import DouyinAdapter
from ..platforms.shipinhao import ShipinhaoAdapter
from ..platforms.bilibili import BilibiliAdapter
from ..platforms import PlatformAdapter
from ..utils.config_loader import load_platform_rules
from .prompts import (
    CREATIVE_ANALYSIS_SYSTEM_PROMPT,
    CREATIVE_ANALYSIS_USER_PROMPT,
    PLATFORM_SCRIPT_SYSTEM_PROMPT,
    PLATFORM_SCRIPT_USER_PROMPT,
    COMPARISON_SYSTEM_PROMPT,
    COMPARISON_USER_PROMPT,
)
from .parser import parse_json_response, validate_script_fields

logger = logging.getLogger(__name__)

ADAPTER_MAP: dict[str, type[PlatformAdapter]] = {
    "douyin": DouyinAdapter,
    "shipinhao": ShipinhaoAdapter,
    "bilibili": BilibiliAdapter,
}


def _build_adapter(platform_key: str) -> PlatformAdapter:
    rules_data = load_platform_rules()
    if platform_key not in rules_data:
        raise ValueError(f"不支持的平台: {platform_key}")
    rule = PlatformRule.from_dict(rules_data[platform_key])
    adapter_cls = ADAPTER_MAP.get(platform_key)
    if adapter_cls is None:
        raise ValueError(f"平台适配器未实现: {platform_key}")
    return adapter_cls(rule)


def run_workflow(
    content: str,
    target_platforms: list[str],
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    options = options or {}
    task_id = str(uuid.uuid4())
    client = get_llm_client()
    generate_images = options.get("generate_images", False)
    adapters: dict[str, PlatformAdapter] = {
        pk: _build_adapter(pk) for pk in target_platforms
    }

    logger.info("[%s] Step 1: 创意解析", task_id)
    creative_analysis = _step_creative_analysis(client, content)

    logger.info("[%s] Step 2: 多平台脚本生成 (%d个平台)", task_id, len(target_platforms))
    platform_results = []
    for pk in target_platforms:
        adapter = adapters[pk]
        script_data = _step_generate_script(
            client, adapter, creative_analysis, content
        )
        plat_result = {
            "platform": pk,
            "platform_name": adapter.rule.name,
            "script": script_data.get("script", script_data),
        }

        if generate_images:
            logger.info("[%s] Step 2b: 为 %s 生成封面图", task_id, pk)
            cover_b64 = _step_generate_cover(
                creative_analysis.get("core_theme", ""),
                plat_result["script"].get("title", ""),
                adapter.rule.key,
            )
            plat_result["cover_image"] = cover_b64

        platform_results.append(plat_result)

    logger.info("[%s] Step 3: 平台差异对比", task_id)
    comparison = _step_compare_platforms(client, platform_results)

    result = {
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "creative_analysis": creative_analysis,
        "platforms": platform_results,
        "platform_comparison": comparison,
    }

    return result


def _step_creative_analysis(client, content: str) -> dict[str, Any]:
    system_prompt = CREATIVE_ANALYSIS_SYSTEM_PROMPT
    user_prompt = CREATIVE_ANALYSIS_USER_PROMPT.format(content=content[:3000])
    raw = client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
    data = parse_json_response(raw)
    defaults = {
        "core_theme": "",
        "key_points": [],
        "target_emotion": "",
        "suggested_hook": "",
        "content_category": "知识科普",
    }
    for k, v in defaults.items():
        data.setdefault(k, v)
    return data


def _step_generate_script(
    client,
    adapter: PlatformAdapter,
    creative: dict[str, Any],
    original_content: str,
) -> dict[str, Any]:
    key_points_str = ", ".join(creative.get("key_points", []))
    system_prompt = PLATFORM_SCRIPT_SYSTEM_PROMPT
    user_prompt = PLATFORM_SCRIPT_USER_PROMPT.format(
        platform_context=adapter.get_prompt_context(),
        title_extra=adapter.get_title_prompt_extra(),
        rhythm_extra=adapter.get_rhythm_prompt_extra(),
        storyboard_extra=adapter.get_storyboard_prompt_extra(),
        hashtag_extra=adapter.get_hashtag_prompt_extra(),
        core_theme=creative.get("core_theme", ""),
        key_points=key_points_str,
        target_emotion=creative.get("target_emotion", ""),
        suggested_hook=creative.get("suggested_hook", ""),
        content_category=creative.get("content_category", ""),
        original_content=original_content[:2000],
    )
    raw = client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
    data = parse_json_response(raw)
    return validate_script_fields(data, adapter.rule.key)


def _step_compare_platforms(
    client,
    platform_results: list[dict[str, Any]],
) -> dict[str, Any]:
    summary_lines = []
    for pr in platform_results:
        script = pr.get("script", {})
        summary_lines.append(
            f"--- {pr.get('platform_name', pr.get('platform'))} ---\n"
            f"标题: {script.get('title', '')}\n"
            f"标签: {', '.join(script.get('hashtags', []))}\n"
            f"发布时间: {script.get('publish_time_suggestion', '')}\n"
        )
    platforms_summary = "\n".join(summary_lines)

    raw = client.chat(
        system_prompt=COMPARISON_SYSTEM_PROMPT,
        user_prompt=COMPARISON_USER_PROMPT.format(platforms_summary=platforms_summary),
        temperature=0.4,
    )
    try:
        return parse_json_response(raw)
    except Exception:
        return {"differences": [], "summary": "对比分析生成失败"}


def _step_generate_cover(
    theme: str,
    title: str,
    platform_key: str,
) -> str:
    img_client = get_image_gen_client()
    style_map = {
        "douyin": "抖音风格：大胆撞色、高对比度、悬念感强、适合短视频平台",
        "shipinhao": "视频号风格：温暖真实、信任感高、适合中长内容",
        "bilibili": "B站风格：科技感、二次元元素、专业硬核、适合深度内容",
    }
    style = style_map.get(platform_key, "电影感")
    return img_client.generate_cover(
        script_title=title,
        content_theme=f"{theme}，{style}",
    )