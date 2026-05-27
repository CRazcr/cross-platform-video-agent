import pytest
from src.agent.prompts import (
    CREATIVE_ANALYSIS_SYSTEM_PROMPT,
    CREATIVE_ANALYSIS_USER_PROMPT,
    PLATFORM_SCRIPT_SYSTEM_PROMPT,
    PLATFORM_SCRIPT_USER_PROMPT,
    COMPARISON_SYSTEM_PROMPT,
    COMPARISON_USER_PROMPT,
)


class TestCreativeAnalysisPrompts:
    def test_system_prompt_not_empty(self):
        assert len(CREATIVE_ANALYSIS_SYSTEM_PROMPT) > 50

    def test_user_prompt_has_content_placeholder(self):
        assert "{content}" in CREATIVE_ANALYSIS_USER_PROMPT

    def test_user_prompt_format(self):
        formatted = CREATIVE_ANALYSIS_USER_PROMPT.format(content="测试内容")
        assert "测试内容" in formatted
        assert "core_theme" in formatted


class TestPlatformScriptPrompts:
    def test_system_prompt_not_empty(self):
        assert len(PLATFORM_SCRIPT_SYSTEM_PROMPT) > 50

    def test_user_prompt_has_placeholders(self):
        required = [
            "{platform_context}", "{title_extra}", "{rhythm_extra}",
            "{storyboard_extra}", "{hashtag_extra}", "{core_theme}",
            "{key_points}", "{target_emotion}", "{suggested_hook}",
            "{content_category}", "{original_content}",
        ]
        for placeholder in required:
            assert placeholder in PLATFORM_SCRIPT_USER_PROMPT, f"缺少占位符: {placeholder}"


class TestComparisonPrompts:
    def test_system_prompt_not_empty(self):
        assert len(COMPARISON_SYSTEM_PROMPT) > 50

    def test_user_prompt_has_placeholder(self):
        assert "{platforms_summary}" in COMPARISON_USER_PROMPT