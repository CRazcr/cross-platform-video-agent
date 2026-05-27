from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from src.agent.workflow import run_workflow
from src.utils.validator import validate_input, CLARIFICATION_QUESTIONS
from src.utils.reporter import generate_json_report, generate_markdown_report
from src.agent.parser import ParseError
from src.llm.image_gen import get_image_gen_client
from src.llm.image_gen import ImageGenClient

st.set_page_config(
    page_title="跨平台短视频脚本智能体",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* ── 全局字体与背景 ── */
    :root {
        --bg-primary: #e8f4fd;
        --bg-secondary: #f5f9ff;
        --bg-card: #ffffff;
        --accent: #667eea;
        --accent-light: #8b5cf6;
        --accent-glow: rgba(102,126,234,0.15);
        --text-primary: #1a2a3a;
        --text-secondary: #5a6a7a;
        --border: rgba(100,120,180,0.12);
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }

    [data-theme="dark"] {
        --bg-primary: #0f1117;
        --bg-secondary: #161b27;
        --bg-card: #1e2436;
        --accent: #6366f1;
        --accent-light: #818cf8;
        --accent-glow: rgba(99,102,241,0.25);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border: rgba(255,255,255,0.08);
    }

    html, body, .stApp { background: #e8f4fd; color: #1a2a3a; }

    /* ── 顶部渐变横幅 ── */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 18px;
        padding: 2.5rem 2rem 2rem;
        margin-bottom: 1.8rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(102,126,234,0.35);
    }
    .hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    .hero h1 {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 0.4rem;
        letter-spacing: -0.5px;
        position: relative;
    }
    .hero p {
        color: rgba(255,255,255,0.75);
        font-size: 1rem;
        margin: 0;
        position: relative;
    }
    .hero .badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.78rem;
        color: #e0e7ff;
        margin-top: 0.8rem;
        position: relative;
    }

    /* ── 卡片通用样式 ── */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        transition: box-shadow 0.2s ease;
    }
    .card:hover { box-shadow: 0 4px 24px rgba(0,0,0,0.18); }
    .card-title {
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--accent-light);
        margin-bottom: 1rem;
    }
    .card h3 { font-size: 1.1rem; font-weight: 700; margin: 0 0 0.5rem; color: var(--text-primary); }
    .card p { color: var(--text-secondary); font-size: 0.9rem; margin: 0; line-height: 1.6; }

    /* ── 平台标签 ── */
    .platform-tag {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: var(--accent-glow);
        border: 1px solid var(--accent);
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        color: var(--accent-light);
        font-weight: 600;
    }

    /* ── 分镜表格 ── */
    .storyboard-table table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    .storyboard-table th {
        background: var(--accent);
        color: white;
        padding: 8px 12px;
        text-align: left;
        font-weight: 600;
    }
    .storyboard-table td {
        padding: 8px 12px;
        border-bottom: 1px solid var(--border);
        color: var(--text-primary);
    }
    .storyboard-table tr:nth-child(even) td { background: rgba(255,255,255,0.02); }

    /* ── 按钮美化 ── */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.2s ease;
        border: none;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px var(--accent-glow);
    }

    /* ── 分隔线 ── */
    hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

    /* ── Tabs 美化 ── */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* ── 平台对比表格 ── */
    .comparison-table table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
    }
    .comparison-table th {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 10px 14px;
        font-weight: 700;
    }
    .comparison-table td {
        padding: 10px 14px;
        border-bottom: 1px solid var(--border);
        color: var(--text-primary);
    }
    .comparison-table tr:nth-child(even) td { background: rgba(255,255,255,0.025); }

    /* ── 进度动画 ── */
    @keyframes pulse-glow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    .loading-text { animation: pulse-glow 1.5s infinite; }

    /* ── 侧边栏美化 ── */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border);
        padding: 1.5rem 1rem;
    }

    /* ── 响应式布局修复 ── */
    .main .block-container { padding-top: 1rem; padding-bottom: 2rem; }

    /* ── 下载按钮行间距 ── */
    [data-testid="stHorizontalBlock"] { gap: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ── 顶部英雄区 ──
st.markdown("""
<div class="hero">
    <h1>🎬 跨平台短视频脚本智能体</h1>
    <p>一个核心创意，一键生成适配抖音 · 视频号 · B站 的差异化脚本</p>
    <span class="badge">Powered by DeepSeek · 适配器架构 · 平台规则引擎</span>
</div>
""", unsafe_allow_html=True)

# ── 侧边栏配置 ──
with st.sidebar:
    st.markdown("### ⚙️ 脚本生成配置")

    st.markdown("**🎯 目标平台**（至少选1个）")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        douyin_on = st.checkbox("📱 抖音", value=True)
    with col_s2:
        shipinhao_on = st.checkbox("📱 视频号", value=True)
    bilibili_on = st.checkbox("📺 B站", value=True)

    target_platforms = []
    if douyin_on: target_platforms.append("douyin")
    if shipinhao_on: target_platforms.append("shipinhao")
    if bilibili_on: target_platforms.append("bilibili")

    if not target_platforms:
        st.warning("请至少选择一个目标平台")

    st.markdown("---")

    st.markdown("**🧩 高级选项**")
    tone = st.selectbox(
        "内容调性",
        ["自动判断", "幽默风趣", "严肃专业", "温暖感人", "悬疑反转", "实用干货"],
        label_visibility="collapsed",
    )
    generate_images = st.toggle("🖼️ 生成预览图（DALL·E 3）", value=False, help="为每个平台生成封面预览图，会增加调用时间")
    audience = st.text_input("目标受众", placeholder="如：18-25岁大学生", help="为空则自动推断")
    extra = st.text_area(
        "补充要求",
        placeholder="如：需要融入产品推广...",
        label_visibility="collapsed",
        height=80,
    )

    st.markdown("---")
    st.caption("🔑 LLM: DeepSeek Chat")
    st.caption("📦 飞书: config/feishu_config.json")

# ── 输入区 + 结果区 ──
tab_input, tab_guide = st.tabs(["✏️ 创作输入", "📖 使用指南"])

with tab_input:
    input_col, result_col = st.columns([1, 1.6], gap="large")

    with input_col:
        st.markdown("### 📝 输入创作内容")

        user_content = st.text_area(
            "在此输入主题或脚本草稿...",
            placeholder=(
                "示例：夏日防晒误区科普\n\n"
                "很多人以为SPF值越高越好，其实SPF30已经能阻挡97%的紫外线。"
                "阴天不需要防晒也是错的，云层只能阻挡20%紫外线...\n\n"
                "也可以上传完整的脚本草稿，或在右侧查看使用指南。"
            ),
            height=320,
            label_visibility="collapsed",
        )

        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            generate_btn = st.button("🚀 生成多平台脚本", type="primary", use_container_width=True)
        with col_b2:
            clear_btn = st.button("🗑️ 清空", use_container_width=True)

        if clear_btn:
            st.session_state.pop("workflow_result", None)
            st.rerun()

        st.caption("💡 内容越详细，生成效果越好。建议至少20字以上。")

    with result_col:
        st.markdown("### 📊 生成结果")

        if generate_btn:
            if not target_platforms:
                st.error("⚠️ 请先在左侧选择至少一个目标平台")
                st.stop()
            if not user_content or len(user_content.strip()) < 10:
                st.error("⚠️ 输入内容过短，请补充更多细节（至少10字）")
                st.stop()

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
                    for q in CLARIFICATION_QUESTIONS:
                        st.write(f"- {q}")
            else:
                options = {}
                if tone and tone != "自动判断":
                    options["tone"] = tone
                if audience:
                    options["target_audience"] = audience
                if extra:
                    options["extra_requirements"] = extra
                options["generate_images"] = generate_images

                with st.spinner("🤖 **AI 正在处理中...**\n\n`Step 1` 创意解析 → `Step 2` 多平台脚本生成 → `Step 3` 差异对比分析"):
                    try:
                        result = run_workflow(
                            content=validation.content,
                            target_platforms=target_platforms,
                            options=options,
                        )
                        st.session_state["workflow_result"] = result
                        st.success(f"✅ 生成完成！任务ID: `{result['task_id'][:8]}`")
                        st.balloons()
                    except ParseError as e:
                        st.error(f"❌ 模型输出解析失败: {e}")
                    except RuntimeError as e:
                        st.error(f"❌ LLM 调用异常: {e}")
                    except Exception as e:
                        st.error(f"❌ 处理异常: {e}")

    if "workflow_result" in st.session_state:
        result = st.session_state["workflow_result"]
        platform_names = [p.get("platform_name", p.get("platform")) for p in result["platforms"]]

        tabs = (
            ["💡 创意解析"]
            + [f"🎬 {name}" for name in platform_names]
            + ["📋 平台对比"]
        )
        tab_creative, *platform_tabs, tab_compare = st.tabs(tabs)

        # ── 创意解析 ──
        with tab_creative:
            creative = result.get("creative_analysis", {})
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**🎯 核心主题**")
                st.info(creative.get("core_theme", "N/A"))
            with cols[1]:
                st.markdown("**🏷️ 内容分类**")
                st.info(creative.get("content_category", "N/A"))
            cols2 = st.columns(2)
            with cols2[0]:
                st.markdown("**🎭 目标情绪**")
                st.info(creative.get("target_emotion", "N/A"))
            with cols2[1]:
                st.markdown("**🪝 推荐开场钩子**")
                st.warning(creative.get("suggested_hook", "N/A"))

            st.markdown("**📌 关键要点**")
            points = creative.get("key_points", [])
            if points:
                for i, pt in enumerate(points, 1):
                    st.markdown(f"{i}. {pt}")
            else:
                st.info("无")

        # ── 各平台脚本 ──
        for tab, plat_data in zip(platform_tabs, result["platforms"]):
            with tab:
                script = plat_data.get("script", {})
                plat_name = plat_data.get("platform_name", plat_data.get("platform", ""))

                cover_b64 = plat_data.get("cover_image", "")
                if cover_b64:
                    st.markdown("**🖼️ AI 封面预览**")
                    img_bytes = ImageGenClient.b64_to_bytes(cover_b64)
                    st.image(img_bytes, use_container_width=True, clamp=True)
                    c_dl, c_copy = st.columns(2)
                    with c_dl:
                        st.download_button(
                            "⬇️ 下载封面图",
                            data=img_bytes,
                            file_name=f"cover_{plat_name}_{result['task_id'][:8]}.png",
                            mime="image/png",
                            use_container_width=True,
                        )
                    st.markdown("---")

                st.markdown(f"**📌 {plat_name} 适配标题**")
                st.code(script.get("title", "N/A"), language=None)

                st.markdown("**✍️ 节奏化文案**")
                rhythm = script.get("rhythm_text", "")
                for para in rhythm.split("\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("【"):
                        st.markdown(f"**{para}**")
                    else:
                        st.markdown(para)

                st.markdown("**🎞️ 分镜建议**")
                storyboard = script.get("storyboard", [])
                if storyboard:
                    rows = []
                    for sb in storyboard:
                        rows.append({
                            "场景": sb.get("scene", ""),
                            "时长": sb.get("duration", ""),
                            "画面": sb.get("visual", ""),
                            "音频": sb.get("audio", ""),
                            "字幕": sb.get("text_overlay", ""),
                        })
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                else:
                    st.info("未生成分镜建议")

                col_h1, col_h2 = st.columns([2, 1])
                with col_h1:
                    st.markdown("**🏷️ 话题标签**")
                    tags = script.get("hashtags", [])
                    st.markdown(" ".join([f"`{tag}`" for tag in tags]))
                with col_h2:
                    st.markdown("**⏰ 发布时间**")
                    st.info(script.get("publish_time_suggestion", "N/A"))

        # ── 平台对比 ──
        with tab_compare:
            comparison = result.get("platform_comparison", {})
            diffs = comparison.get("differences", [])
            if diffs:
                headers = ["对比维度"] + platform_names
                rows = []
                for d in diffs:
                    row = [d.get("aspect", "")]
                    for p in result["platforms"]:
                        row.append(d.get(p.get("platform", ""), ""))
                    rows.append(row)
                df = pd.DataFrame(rows, columns=headers)
                st.dataframe(df, use_container_width=True, hide_index=True)

            summary = comparison.get("summary", "")
            if summary:
                st.markdown("**📝 核心差异总结**")
                st.info(summary)

        # ── 导出区域 ──
        st.markdown("---")
        st.markdown("### 📥 导出报告")

        json_report = generate_json_report(result)
        md_report = generate_markdown_report(result)
        task_id = result["task_id"][:8]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "📄 JSON 报告",
                data=json_report,
                file_name=f"video_script_{task_id}.json",
                mime="application/json",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "📝 Markdown 报告",
                data=md_report,
                file_name=f"video_script_{task_id}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with c3:
            if st.button("📬 发布到飞书", use_container_width=True):
                try:
                    from src.feishu.publisher import publish_to_feishu
                    title = result["creative_analysis"].get("core_theme", "短视频脚本")
                    feishu_result = publish_to_feishu(title, md_report)
                    if feishu_result.get("document", {}).get("status") == "success":
                        st.success(f"已发布到飞书: {feishu_result['document']['url']}")
                    else:
                        st.warning("飞书发布失败，请检查配置")
                except Exception as e:
                    st.error(f"飞书异常: {e}")

with tab_guide:
    st.markdown("### 📖 使用指南")
    guide_col1, guide_col2 = st.columns(2)
    with guide_col1:
        st.markdown("""
        **🔹 第一步：输入内容**
        - 直接在左侧输入框输入创作主题描述
        - 或上传 `.txt` / `.md` 格式的脚本草稿
        - 内容越详细，生成质量越高
        """)
        st.markdown("""
        **🔹 第二步：选择平台**
        - 至少勾选 1 个目标平台
        - 支持抖音 / 视频号 / B站 同时生成
        """)
    with guide_col2:
        st.markdown("""
        **🔹 第三步：调整选项**
        - 内容调性：决定文案的说话风格
        - 目标受众：让 AI 更精准匹配用户画像
        - 补充要求：可添加特殊需求或产品推广元素
        """)
        st.markdown("""
        **🔹 第四步：生成与导出**
        - 点击「🚀 生成多平台脚本」
        - 等待 10-30 秒，查看各平台脚本
        - 下载 JSON/Markdown 报告，或一键发布到飞书
        """)
    st.markdown("---")
    st.markdown("""
    **💡 提示**：
    - 抖音适合快节奏、强情绪、悬念反转类内容
    - 视频号适合真实感强、信任感高的经验分享
    - B站适合深度、专业、有数据支撑的硬核内容
    """)

# ── 底部签名 ──
st.markdown(
    "<div style='text-align:center;color:#475569;font-size:0.8rem;padding:1rem 0;'>"
    "🎬 跨平台短视频脚本适配与优化智能体 · Powered by DeepSeek · "
    "<a href='https://github.com/CRazcr/cross-platform-video-agent' target='_blank' style='color:#667eea;'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True,
)
