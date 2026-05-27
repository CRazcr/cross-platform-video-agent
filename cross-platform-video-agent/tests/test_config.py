import json
import tempfile
from pathlib import Path
import pytest
from src.utils.config_loader import load_json_config, load_platform_rules


class TestLoadJsonConfig:
    def test_load_valid_config(self):
        rules = load_platform_rules()
        assert isinstance(rules, dict)
        assert "douyin" in rules
        assert "shipinhao" in rules
        assert "bilibili" in rules

    def test_platform_rules_structure(self):
        rules = load_platform_rules()
        dy = rules["douyin"]
        assert "name" in dy
        assert "duration_range" in dy
        assert "tone_keywords" in dy
        assert "title_structure" in dy
        assert "content_rules" in dy
        assert dy["title_structure"]["require_hashtags_in_title"] is True

    def test_douyin_golden_3_seconds(self):
        rules = load_platform_rules()
        content_rules = rules["douyin"]["content_rules"]
        assert "golden_3_seconds" in content_rules
        assert "前3秒" in content_rules["golden_3_seconds"]

    def test_bilibili_duration_range(self):
        rules = load_platform_rules()
        bili_dr = rules["bilibili"]["duration_range"]
        assert bili_dr["min_seconds"] == 60
        assert bili_dr["optimal_seconds"] == 300

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_json_config("non_existent_file.json")


class TestConfigConsistency:
    def test_all_platforms_have_required_fields(self):
        rules = load_platform_rules()
        required = ["name", "key", "description", "duration_range", "tone_keywords",
                     "title_structure", "content_rules", "hot_hashtags_examples",
                     "publish_time", "audience_profile"]
        for pk, pr in rules.items():
            for field in required:
                assert field in pr, f"平台 {pk} 缺少字段: {field}"

    def test_platform_keys_match(self):
        rules = load_platform_rules()
        for pk, pr in rules.items():
            assert pr["key"] == pk, f"平台 {pk} 的 key 字段不匹配"