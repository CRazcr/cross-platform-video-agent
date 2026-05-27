from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def generate_json_report(data: dict[str, Any], indent: int = 2) -> str:
    return json.dumps(data, ensure_ascii=False, indent=indent)


def generate_markdown_report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    creative = data.get("creative_analysis", {})

    lines.append("# 跨平台短视频脚本适配报告")
    lines.append("")
    lines.append(f"**生成时间**: {data.get('generated_at', datetime.now().isoformat())}")
    lines.append(f"**任务ID**: {data.get('task_id', 'N/A')}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 创意解析")
    lines.append("")
    lines.append(f"**核心主题**: {creative.get('core_theme', 'N/A')}")
    lines.append("")
    lines.append("**关键要点**:")
    for point in creative.get("key_points", []):
        lines.append(f"- {point}")
    lines.append("")
    lines.append(f"**目标情绪**: {creative.get('target_emotion', 'N/A')}")
    lines.append(f"**推荐钩子**: {creative.get('suggested_hook', 'N/A')}")
    lines.append("")

    platforms = data.get("platforms", [])
    for plat in platforms:
        lines.append("---")
        lines.append("")
        lines.append(f"## {plat.get('platform_name', plat.get('platform', 'Unknown'))} 脚本")
        lines.append("")
        script = plat.get("script", {})

        lines.append(f"### 适配标题")
        lines.append(f"> {script.get('title', 'N/A')}")
        lines.append("")

        lines.append("### 节奏化文案")
        lines.append("")
        rhythm = script.get("rhythm_text", "")
        for paragraph in rhythm.split("\n"):
            lines.append(paragraph)
            lines.append("")
        lines.append("")

        storyboard = script.get("storyboard", [])
        if storyboard:
            lines.append("### 分镜建议")
            lines.append("")
            lines.append("| 场景 | 时长 | 画面 | 音频 | 字幕 |")
            lines.append("|------|------|------|------|------|")
            for sb in storyboard:
                lines.append(
                    f"| {sb.get('scene', '')} "
                    f"| {sb.get('duration', '')} "
                    f"| {sb.get('visual', '')} "
                    f"| {sb.get('audio', '')} "
                    f"| {sb.get('text_overlay', '')} |"
                )
            lines.append("")

        hashtags = script.get("hashtags", [])
        if hashtags:
            lines.append("### 话题标签")
            lines.append("")
            lines.append(" ".join(f"`{tag}`" for tag in hashtags))
            lines.append("")

        pub_time = script.get("publish_time_suggestion", "")
        if pub_time:
            lines.append(f"### 发布时间建议")
            lines.append(f"> {pub_time}")
            lines.append("")

    comparison = data.get("platform_comparison", {})
    if comparison:
        lines.append("---")
        lines.append("")
        lines.append("## 平台差异对比")
        lines.append("")
        diffs = comparison.get("differences", [])
        if diffs:
            headers = ["对比维度"] + [d.get("aspect", "") for d in diffs]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("|" + "|".join(["------"] * len(headers)) + "|")
            for plat in platforms:
                pname = plat.get("platform_name", plat.get("platform", ""))
                row = [pname]
                for d in diffs:
                    row.append(d.get(plat.get("platform", ""), ""))
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")

        summary = comparison.get("summary", "")
        if summary:
            lines.append("### 总结")
            lines.append(summary)
            lines.append("")

    return "\n".join(lines)