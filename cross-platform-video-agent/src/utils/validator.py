from __future__ import annotations

from typing import Optional

MIN_CONTENT_LENGTH = 10
CLARIFICATION_QUESTIONS = [
    "你希望视频面向哪类受众？（如：大学生、职场新人、宝妈等）",
    "这个主题你最想传达的核心观点是什么？",
    "你希望视频的整体风格是怎样的？（如：幽默搞笑、严肃科普、温情故事等）",
]


class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        content: str,
        input_type: str = "topic",
        message: str = "",
        needs_clarification: bool = False,
        clarification_questions: Optional[list[str]] = None,
    ):
        self.is_valid = is_valid
        self.content = content.strip()
        self.input_type = input_type
        self.message = message
        self.needs_clarification = needs_clarification
        self.clarification_questions = clarification_questions or []


def detect_input_type(content: str) -> str:
    content = content.strip()
    draft_keywords = ["开场", "分镜", "旁白", "画面", "镜头", "转场", "BGM", "字幕", "【"]
    keyword_count = sum(1 for kw in draft_keywords if kw in content)
    if keyword_count >= 3:
        return "draft"
    if len(content) > 500:
        return "draft"
    return "topic"


def validate_input(
    content: str,
    target_platforms: list[str],
    options: Optional[dict] = None,
) -> ValidationResult:
    content = content.strip() if content else ""
    platforms = [p.strip().lower() for p in target_platforms if p.strip()]

    if not content:
        return ValidationResult(
            is_valid=False,
            content="",
            message="请输入创作主题或上传脚本草稿。",
            needs_clarification=True,
            clarification_questions=CLARIFICATION_QUESTIONS,
        )

    if len(platforms) < 2:
        return ValidationResult(
            is_valid=False,
            content=content,
            message="请至少选择2个目标平台以进行跨平台适配。",
        )

    valid_platforms = {"douyin", "shipinhao", "bilibili"}
    invalid = [p for p in platforms if p not in valid_platforms]
    if invalid:
        return ValidationResult(
            is_valid=False,
            content=content,
            message=f"不支持的平台: {', '.join(invalid)}。支持的平台: douyin, shipinhao, bilibili",
        )

    input_type = detect_input_type(content)

    if input_type == "topic" and len(content) < MIN_CONTENT_LENGTH:
        return ValidationResult(
            is_valid=False,
            content=content,
            input_type=input_type,
            message=f"输入内容过于简略（少于{MIN_CONTENT_LENGTH}字），请补充更多细节。",
            needs_clarification=True,
            clarification_questions=CLARIFICATION_QUESTIONS,
        )

    return ValidationResult(
        is_valid=True,
        content=content,
        input_type=input_type,
        message="输入验证通过",
    )