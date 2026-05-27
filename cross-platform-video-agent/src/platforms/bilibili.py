from .base import PlatformRule
from . import PlatformAdapter


class BilibiliAdapter(PlatformAdapter):
    def __init__(self, rule: PlatformRule):
        self.rule = rule

    def get_prompt_context(self) -> str:
        return self.rule.to_prompt_context()

    def get_generation_prompt(self) -> str:
        return "为B站平台生成中长视频脚本。B站用户偏好深度、专业、有信息量的内容，喜欢硬核科普和逻辑严密的论证。"

    def get_title_prompt_extra(self) -> str:
        return (
            "B站标题使用【标签】前缀格式，如【硬核科普】【实测】【深度解读】。"
            "标题可以稍长（不超过60字），表达完整的观点或结论。"
            "标题要体现内容的深度和专业性，可以引用数据或文献暗示。"
            "适当使用B站社区梗和流行语增加亲切感。"
            "不需要在标题中嵌入话题标签。"
        )

    def get_rhythm_prompt_extra(self) -> str:
        return (
            "B站文案允许15-30秒的开场铺垫，用数据、故事或问题引入主题。"
            "采用段落式结构，每段深入讲解一个观点（每个段落约30-60秒）。"
            "使用数据、案例、文献来支撑论点，增强可信度和专业感。"
            "设计中至少2-3个弹幕互动点（抛出问题、征集观点、制造梗点）。"
            "结尾总结核心观点，引导观众一键三连和评论区讨论。"
            "全程控制在5分钟以内（约800-1200字文案）。"
        )

    def get_storyboard_prompt_extra(self) -> str:
        return (
            "B站分镜节奏适中，每个镜头5-15秒，允许更丰富的画面设计。"
            "开场可以用深色背景+灯光效果营造专业感。"
            "中间段配合数据图表、文献引用卡片等视觉元素。"
            "建议5-7个分镜，给每个段落留足展示空间。"
        )

    def get_hashtag_prompt_extra(self) -> str:
        return (
            "B站标签以内容领域分类为主，如 #硬核科普 #数码测评 #涨知识。"
            "建议3-5个标签，精准描述内容领域。"
        )