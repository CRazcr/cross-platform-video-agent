from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlatformRule:
    key: str
    name: str
    description: str
    duration_min: int
    duration_max: int
    duration_optimal: int
    tone_keywords: list[str] = field(default_factory=list)
    title_patterns: list[str] = field(default_factory=list)
    title_max_length: int = 50
    title_hashtag_in_title: bool = False
    content_rules: dict[str, str] = field(default_factory=dict)
    hot_hashtags: list[str] = field(default_factory=list)
    best_publish_times: list[str] = field(default_factory=list)
    best_publish_days: str = ""
    publish_note: str = ""
    audience_profile: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlatformRule":
        duration = data.get("duration_range", {})
        title = data.get("title_structure", {})
        publish = data.get("publish_time", {})
        return cls(
            key=data.get("key", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            duration_min=duration.get("min_seconds", 15),
            duration_max=duration.get("max_seconds", 300),
            duration_optimal=duration.get("optimal_seconds", 60),
            tone_keywords=data.get("tone_keywords", []),
            title_patterns=title.get("patterns", []),
            title_max_length=title.get("max_length", 50),
            title_hashtag_in_title=title.get("require_hashtags_in_title", False),
            content_rules=data.get("content_rules", {}),
            hot_hashtags=data.get("hot_hashtags_examples", []),
            best_publish_times=publish.get("best_times", []),
            best_publish_days=publish.get("best_days", ""),
            publish_note=publish.get("note", ""),
            audience_profile=data.get("audience_profile", ""),
        )

    def to_prompt_context(self) -> str:
        lines = [
            f"平台名称: {self.name}",
            f"平台特点: {self.description}",
            f"受众画像: {self.audience_profile}",
            f"最佳时长: {self.duration_optimal}秒 (范围: {self.duration_min}-{self.duration_max}秒)",
            f"内容调性关键词: {', '.join(self.tone_keywords)}",
            f"标题限制: 不超过{self.title_max_length}字",
        ]
        if self.title_hashtag_in_title:
            lines.append("标题要求: 必须在标题中嵌入话题标签")
        if self.content_rules:
            rules = "; ".join(f"{k}: {v}" for k, v in self.content_rules.items())
            lines.append(f"内容规则: {rules}")
        if self.best_publish_times:
            lines.append(f"最佳发布时间: {', '.join(self.best_publish_times)}; {self.publish_note}")
            lines.append(f"最佳发布日: {self.best_publish_days}")
        if self.hot_hashtags:
            lines.append(f"热门标签参考: {', '.join(self.hot_hashtags)}")
        return "\n".join(lines)