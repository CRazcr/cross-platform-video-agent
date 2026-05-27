import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.workflow import run_workflow
from src.utils.validator import validate_input, CLARIFICATION_QUESTIONS
from src.utils.reporter import generate_json_report, generate_markdown_report
from src.agent.parser import ParseError

st.set_page_config(
    page_title="跨平台短视频脚本适配与优化智能体",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎬 跨平台短视频脚本适配与优化智能体")
st.caption("一个核心创意 → 一键生成适配抖音、视频号、B站的多平台差异化脚本")

with st.sidebar:
    st.header("⚙️ 配置")

    st.subheader("目标平台")
    platform_douyin = st.checkbox("抖音", value=True, help="15s-3min，快节奏强情绪")
    platform_shipinhao = st.checkbox("视频号", value=True, help="30s-5min，熟人社交传播")
    platform_bilibili = st.checkbox("B站", value=True, help="1min-15min，深度内容社区")

    target_platforms = []
    if platform_douyin:
        target_platforms.append("douyin")
    if platform_shipinhao:
        target_platforms.append("shipinhao")
    if platform_bilibili:
        target_platforms.append("bilibili")

    st.divider()

    st.subheader("高级选项")
    with st.expander("展开设置"):
        tone = st.selectbox(
            "内容调性",
            ["自动判断", "幽默风趣", "严肃专业", "温暖感人", "悬疑反转", "实用干货"],
            index=0,
        )
        audience = st.text_input("目标受众", placeholder="如：18-25岁大学生")
        extra = st.text_area("补充要求", placeholder="如：需要融入产品推广元素...", height=80)

    st.divider()
    st.caption("Powered by DeepSeek API")
    st.caption("飞书集成：config/feishu_config.json")

col_input, col_preview = st.columns([1, 1.5])

with col_input:
    st.header("📝 输入创作内容")

    input_tab1, input_tab2 = st.tabs(["✏️ 直接输入", "📎 上传文件"])

    with input_tab1:
        user_content = st.text_area(
            "输入创作主题或脚本草稿",
            placeholder="例如：夏日防晒误区科普\n\n很多人以为SPF值越高越好，其实SPF30已经能阻挡97%的紫外线...\n\n也可以是完整的脚本草稿...",
            height=250,
        )

    with input_tab2:
        uploaded_file = st.file_uploader(
            "上传脚本草稿（.txt / .md）",
            type=["txt", "md"],
            help="支持纯文本和Markdown格式",
        )
        if uploaded_file is not None:
            user_content = uploaded_file.read().decode("utf-8")
            st.text_area("文件内容预览", user_content, height=200, disabled=True)

    col_btn1, col_btn2 = st.columns([3, 1])

    with col_btn1:
        generate_btn = st.button(
            "🚀 生成多平台脚本",
            type="primary",
            use_container_width=True,
        )

    with col_btn2:
        clear_btn = st.button("清空", use_container_width=True)
        if clear_btn:
            st.session_state.pop("workflow_result", None)
            st.rerun()

with col_preview:
    st.header("📊 生成结果")

    if generate_btn:
        validation = validate_input(
            content=user_content,
            target_platforms=target_platforms,
            options={
                "tone": tone if tone != "自动判断" else None,
                "target_audience": audience or None,
                "extra_requirements": extra or None,
            },
        )

        if not validation.is_valid:
            st.error(validation.message)
            if validation.needs_clarification:
                st.info("💡 请补充以下信息：")
                for q in validation.clarification_questions:
                    st.write(f"- {q}")
        else:
            with st.spinner("🤖 正在处理中...\n\nStep 1: 创意解析\nStep 2: 多平台脚本生成\nStep 3: 差异对比分析"):
                try:
                    options = {}
                    if tone and tone != "自动判断":
                        options["tone"] = tone
                    if audience:
                        options["target_audience"] = audience
                    if extra:
                        options["extra_requirements"] = extra

                    result = run_workflow(
                        content=validation.content,
                        target_platforms=target_platforms,
                        options=options,
                    )
                    st.session_state["workflow_result"] = result
                    st.success(f"✅ 生成完成！任务ID: {result['task_id'][:8]}...")
                    st.balloons()
                except ParseError as e:
                    st.error(f"❌ 模型输出解析失败: {e}")
                except RuntimeError as e:
                    st.error(f"❌ LLM 调用异常: {e}")
                except Exception as e:
                    st.error(f"❌ 处理异常: {e}")

    if "workflow_result" in st.session_state:
        result = st.session_state["workflow_result"]

        tab_creative, *platform_tabs, tab_compare = st.tabs(
            ["💡 创意解析"]
            + [
                f"🎬 {p.get('platform_name', p.get('platform'))}"
                for p in result["platforms"]
            ]
            + ["📋 平台对比"]
        )

        with tab_creative:
            creative = result.get("creative_analysis", {})
            st.subheader("核心解读")
            st.markdown(f"**核心主题**: {creative.get('core_theme', 'N/A')}")
            st.markdown(f"**内容分类**: {creative.get('content_category', 'N/A')}")
            st.markdown(f"**目标情绪**: {creative.get('target_emotion', 'N/A')}")
            st.markdown(f"**推荐开场钩子**: _{creative.get('suggested_hook', 'N/A')}_")

            st.subheader("关键要点")
            for i, point in enumerate(creative.get("key_points", []), 1):
                st.markdown(f"{i}. {point}")

        for tab, plat_data in zip(platform_tabs, result["platforms"]):
            with tab:
                script = plat_data.get("script", {})
                st.subheader("📌 适配标题")
                st.code(script.get("title", "N/A"), language=None)

                st.subheader("✍️ 节奏化文案")
                rhythm = script.get("rhythm_text", "")
                for para in rhythm.split("\n"):
                    para = para.strip()
                    if para:
                        if para.startswith("【"):
                            st.markdown(f"**{para}**")
                        else:
                            st.markdown(para)

                st.subheader("🎞️ 分镜建议")
                storyboard = script.get("storyboard", [])
                if storyboard:
                    sb_data = []
                    for sb in storyboard:
                        sb_data.append(
                            {
                                "场景": sb.get("scene", ""),
                                "时长": sb.get("duration", ""),
                                "画面": sb.get("visual", ""),
                                "音频": sb.get("audio", ""),
                                "字幕": sb.get("text_overlay", ""),
                            }
                        )
                    st.dataframe(sb_data, use_container_width=True)
                else:
                    st.info("未生成分镜建议")

                st.subheader("🏷️ 话题标签")
                hashtags = script.get("hashtags", [])
                st.markdown(" ".join([f"`{tag}`" for tag in hashtags]))

                st.subheader("⏰ 发布时间建议")
                st.info(script.get("publish_time_suggestion", "N/A"))

        with tab_compare:
            comparison = result.get("platform_comparison", {})
            diffs = comparison.get("differences", [])
            if diffs:
                headers = ["对比维度"] + [
                    p.get("platform_name", p.get("platform"))
                    for p in result["platforms"]
                ]
                rows = []
                for d in diffs:
                    row = [d.get("aspect", "")]
                    for p in result["platforms"]:
                        row.append(d.get(p.get("platform", ""), ""))
                    rows.append(row)

                import pandas as pd
                df = pd.DataFrame(rows, columns=headers)
                st.dataframe(df, use_container_width=True, hide_index=True)

            summary = comparison.get("summary", "")
            if summary:
                st.subheader("核心差异总结")
                st.info(summary)

        st.divider()
        st.subheader("📥 导出")

        col_export1, col_export2, col_export3 = st.columns(3)

        json_report = generate_json_report(result)
        md_report = generate_markdown_report(result)

        with col_export1:
            st.download_button(
                label="📄 下载 JSON 报告",
                data=json_report,
                file_name=f"video_script_{result['task_id'][:8]}.json",
                mime="application/json",
                use_container_width=True,
            )

        with col_export2:
            st.download_button(
                label="📝 下载 Markdown 报告",
                data=md_report,
                file_name=f"video_script_{result['task_id'][:8]}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col_export3:
            if st.button("📄 发布到飞书", use_container_width=True):
                try:
                    from src.feishu.publisher import publish_to_feishu

                    title = result["creative_analysis"].get("core_theme", "短视频脚本")
                    feishu_result = publish_to_feishu(title, md_report)
                    if feishu_result.get("document", {}).get("status") == "success":
                        st.success(
                            f"已发布到飞书文档: {feishu_result['document']['url']}"
                        )
                    else:
                        st.warning("飞书发布失败或未启用，请检查配置")
                except Exception as e:
                    st.error(f"飞书集成异常: {e}")