import pytest
from src.utils.validator import validate_input, detect_input_type, CLARIFICATION_QUESTIONS


class TestDetectInputType:
    def test_detect_topic_short_text(self):
        assert detect_input_type("夏日防晒误区科普") == "topic"

    def test_detect_draft_with_keywords(self):
        content = "开场：大家好我是XX\n分镜1：特写产品\n旁白：今天来聊聊防晒\nBGM：轻松愉快"
        assert detect_input_type(content) == "draft"

    def test_detect_draft_long_text(self):
        content = "这是一个非常长的输入内容" * 100
        assert detect_input_type(content) == "draft"


class TestValidateInput:
    def test_empty_content(self):
        result = validate_input("", ["douyin", "shipinhao"])
        assert not result.is_valid
        assert result.needs_clarification

    def test_too_few_platforms(self):
        result = validate_input("测试科普主题内容", ["douyin"])
        assert not result.is_valid
        assert "至少选择2个" in result.message

    def test_invalid_platform(self):
        result = validate_input("测试科普主题内容", ["douyin", "xiaohongshu"])
        assert not result.is_valid
        assert "不支持" in result.message

    def test_too_short_topic(self):
        result = validate_input("短", ["douyin", "bilibili"])
        assert not result.is_valid
        assert result.needs_clarification

    def test_valid_topic_input(self):
        result = validate_input(
            "夏日防晒误区科普：很多人都不知道阴天也需要涂防晒霜",
            ["douyin", "bilibili"],
        )
        assert result.is_valid
        assert result.input_type == "topic"

    def test_valid_draft_input(self):
        content = """开场：【画面】人物出镜
分镜1：【特写】产品展示，BGM卡点节奏
旁白：今天来聊聊一个99%的人都不知道的防晒误区"""
        result = validate_input(content, ["douyin", "shipinhao", "bilibili"])
        assert result.is_valid
        assert result.input_type == "draft"

    def test_whitespace_content(self):
        result = validate_input("   \n  ", ["douyin", "bilibili"])
        assert not result.is_valid


class TestClarificationQuestions:
    def test_questions_exist(self):
        result = validate_input("短", ["douyin", "bilibili"])
        assert len(result.clarification_questions) > 0
        assert result.clarification_questions == CLARIFICATION_QUESTIONS