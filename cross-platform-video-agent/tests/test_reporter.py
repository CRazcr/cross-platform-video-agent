import json
from src.utils.reporter import generate_json_report, generate_markdown_report


SAMPLE_RESULT = {
    "task_id": "test-1234-5678",
    "generated_at": "2026-05-27T10:00:00Z",
    "creative_analysis": {
        "core_theme": "夏日防晒误区科普",
        "key_points": ["SPF并非越高越好", "阴天也需防晒", "物理与化学防晒差异"],
        "target_emotion": "好奇→惊讶→认同→行动",
        "suggested_hook": "90%的人防晒都做错了！",
        "content_category": "知识科普",
    },
    "platforms": [
        {
            "platform": "douyin",
            "platform_name": "抖音",
            "script": {
                "title": "防晒SPF越高越好？错了！#防晒误区",
                "rhythm_text": "【0-3s】你每年防晒钱可能白花了！\n【3-15s】SPF30=97%防护",
                "storyboard": [
                    {"scene": 1, "duration": "0-3s", "visual": "惊讶特写", "audio": "快节奏BGM", "text_overlay": "标题"}
                ],
                "hashtags": ["#防晒误区", "#护肤科普"],
                "publish_time_suggestion": "12:00-13:00",
            },
        },
        {
            "platform": "bilibili",
            "platform_name": "B站",
            "script": {
                "title": "【硬核科普】防晒常识可能全是错的！",
                "rhythm_text": "【0-15s】开场引入\n【15-60s】数据展示",
                "storyboard": [
                    {"scene": 1, "duration": "0-15s", "visual": "深色背景+灯光", "audio": "科技感BGM", "text_overlay": "标题"}
                ],
                "hashtags": ["#硬核科普", "#防晒"],
                "publish_time_suggestion": "周五18:00-20:00",
            },
        },
    ],
    "platform_comparison": {
        "differences": [
            {"aspect": "时长", "douyin": "45秒", "bilibili": "5分钟"},
            {"aspect": "风格", "douyin": "快节奏", "bilibili": "深度科普"},
        ],
        "summary": "抖音追求快节奏高密度，B站追求深度和专业性。",
    },
}


class TestGenerateJsonReport:
    def test_generate_valid_json(self):
        report = generate_json_report(SAMPLE_RESULT)
        data = json.loads(report)
        assert data["task_id"] == "test-1234-5678"
        assert len(data["platforms"]) == 2

    def test_json_indent(self):
        report = generate_json_report(SAMPLE_RESULT, indent=4)
        assert "    " in report


class TestGenerateMarkdownReport:
    def test_generate_md_contains_title(self):
        report = generate_markdown_report(SAMPLE_RESULT)
        assert "# 跨平台短视频脚本适配报告" in report

    def test_generate_md_contains_platform_names(self):
        report = generate_markdown_report(SAMPLE_RESULT)
        assert "抖音" in report
        assert "B站" in report

    def test_generate_md_contains_comparison(self):
        report = generate_markdown_report(SAMPLE_RESULT)
        assert "平台差异对比" in report

    def test_generate_md_return_type(self):
        report = generate_markdown_report(SAMPLE_RESULT)
        assert isinstance(report, str)
        assert len(report) > 100