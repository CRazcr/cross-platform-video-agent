from .base import PlatformRule
from . import PlatformAdapter


class DouyinAdapter(PlatformAdapter):
    def __init__(self, rule: PlatformRule):
        self.rule = rule

    def get_prompt_context(self) -> str:
        return self.rule.to_prompt_context()

    def get_generation_prompt(self) -> str:
        return "为抖音平台生成短视频脚本。抖音是快节奏短视频平台，受众广泛，内容需要在极短时间内抓住注意力。"

    def get_title_prompt_extra(self) -> str:
        return (
            "抖音标题必须制造悬念或强烈好奇心，使用反问、数字罗列、结果前置等手法。"
            "标题中必须包含2-3个热门话题标签（如 #涨知识 #干货）。"
            "标题不超过50字，要让人看到就想点击。"
            "标题要有网感，使用口语化表达和网络热词。"
        )

    def get_rhythm_prompt_extra(self) -> str:
        return (
            "抖音文案必须遵循黄金3秒法则：前3秒用视觉冲击或悬念抓住用户。"
            "每5-8秒一个信息点或反转，全程高密度输出。"
            "使用短句，口语化表达，大量使用感叹号和疑问句制造情绪起伏。"
            "结尾要引导关注、点赞、评论，并预告下期内容。"
            "全程控制在45秒以内（约150-200字文案）。"
        )

    def get_storyboard_prompt_extra(self) -> str:
        return (
            "抖音分镜要求快节奏卡点，每个镜头2-5秒。"
            "必须设计一个视觉冲击力强的开场镜头（0-3秒）。"
            "文字字幕要大且醒目，配合快节奏BGM。"
            "建议4-6个分镜。"
        )

    def get_hashtag_prompt_extra(self) -> str:
        return (
            "抖音标签要兼顾热门大标签和精准小标签，共5-8个。"
            "大标签如 #涨知识 #干货分享 获取泛流量，小标签精准触达目标人群。"
        )