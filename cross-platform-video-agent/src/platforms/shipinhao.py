from .base import PlatformRule
from . import PlatformAdapter


class ShipinhaoAdapter(PlatformAdapter):
    def __init__(self, rule: PlatformRule):
        self.rule = rule

    def get_prompt_context(self) -> str:
        return self.rule.to_prompt_context()

    def get_generation_prompt(self) -> str:
        return "为微信视频号平台生成短视频脚本。视频号内容基于熟人社交传播，强调真实感、信任感和实用性。"

    def get_title_prompt_extra(self) -> str:
        return (
            "视频号标题风格偏真实和实用，像朋友分享经验，不要太浮夸。"
            "适合使用'经验分享'、'大实话'、'手把手教你'等真诚表达。"
            "标题不超过40字，不需要嵌入话题标签。"
            "强调内容的实用价值和收藏意义。"
        )

    def get_rhythm_prompt_extra(self) -> str:
        return (
            "视频号文案以娓娓道来的方式展开，不需要刻意追求快节奏。"
            "开头以真实经历或生活场景自然引入，建立亲切感和信任感。"
            "中间段落式展开，每段讲清楚一个实用知识点。"
            "结尾引导转发给朋友或朋友圈，强调实用性和可收藏价值。"
            "全程控制在90秒以内（约250-350字文案）。"
        )

    def get_storyboard_prompt_extra(self) -> str:
        return (
            "视频号分镜节奏舒缓自然，每个镜头5-10秒。"
            "开场以真实生活场景或博主出镜为主，不要过度设计。"
            "画面风格温暖、真实，避免过度滤镜和特效。"
            "建议4-5个分镜。"
        )

    def get_hashtag_prompt_extra(self) -> str:
        return (
            "视频号标签偏实用和生活化，如 #实用技巧 #生活小窍门。"
            "建议3-5个标签，注重内容分类而非流量获取。"
        )