import json
import pytest
from src.agent.parser import parse_json_response, validate_script_fields, ParseError


class TestParseJsonResponse:
    def test_parse_valid_json(self):
        data = parse_json_response('{"key": "value", "num": 123}')
        assert data["key"] == "value"
        assert data["num"] == 123

    def test_parse_json_with_markdown_wrapper(self):
        raw = '''
```json
{"title": "测试标题", "content": "测试内容"}
```
'''
        data = parse_json_response(raw)
        assert data["title"] == "测试标题"

    def test_parse_json_with_extra_text(self):
        raw = '这是一些说明文字 {"result": "success"} 后面还有文字'
        data = parse_json_response(raw)
        assert data["result"] == "success"

    def test_parse_invalid_json_raises_error(self):
        with pytest.raises(ParseError):
            parse_json_response("这不是JSON内容也不是有效的格式", max_retries=0)

    def test_parse_empty_json(self):
        data = parse_json_response("{}")
        assert isinstance(data, dict)
        assert len(data) == 0


class TestValidateScriptFields:
    def test_all_fields_present(self):
        data = {
            "script": {
                "title": "测试标题",
                "rhythm_text": "测试文案",
                "storyboard": [{"scene": 1, "duration": "0-3s", "visual": "特写", "audio": "BGM", "text_overlay": "标题"}],
                "hashtags": ["#测试", "#脚本"],
                "publish_time_suggestion": "12:00",
            }
        }
        result = validate_script_fields(data, "douyin")
        assert result["script"]["title"] == "测试标题"

    def test_missing_fields_get_defaults(self):
        data = {"script": {"title": "只有标题"}}
        result = validate_script_fields(data, "douyin")
        script = result["script"]
        assert script["title"] == "只有标题"
        assert script["rhythm_text"] == "未生成文案"
        assert script["storyboard"] == []
        assert script["hashtags"] == []
        assert script["publish_time_suggestion"] == ""

    def test_hashtags_string_to_list(self):
        data = {"script": {"title": "测试", "hashtags": "#单个标签"}}
        result = validate_script_fields(data, "douyin")
        assert isinstance(result["script"]["hashtags"], list)

    def test_top_level_without_script_key(self):
        data = {
            "title": "直接标题",
            "rhythm_text": "直接文案",
            "storyboard": [],
            "hashtags": ["#tag"],
            "publish_time_suggestion": "12:00",
        }
        result = validate_script_fields(data, "douyin")
        assert "script" in result
        assert result["script"]["title"] == "直接标题"


class TestExtractJson:
    def test_nested_json(self):
        raw = '{"outer": {"inner": {"deep": "value"}}}'
        data = parse_json_response(raw)
        assert data["outer"]["inner"]["deep"] == "value"

    def test_json_array_returns_list(self):
        result = parse_json_response('[1, 2, 3]', max_retries=0)
        assert isinstance(result, list)
        assert result == [1, 2, 3]

    def test_unicode_content(self):
        raw = '{"标题": "中文测试", "标签": ["#科普", "#学习"]}'
        data = parse_json_response(raw)
        assert data["标题"] == "中文测试"
        assert len(data["标签"]) == 2