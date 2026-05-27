# 跨平台短视频脚本适配与优化智能体

一个核心创意 → 一键生成适配**抖音、视频号、B站**的多平台差异化短视频脚本。

## 项目简介

帮助短视频创作者将同一核心创意，基于各平台的算法规则和用户偏好，自动生成风格各异的优化脚本。每个脚本结构化包含：适配标题、节奏化文案、分镜建议、话题标签、发布时间建议，并提供平台差异对比分析。

## 功能特性

- **智能输入识别**：自动区分"主题描述"和"脚本草稿"两种输入模式
- **三平台适配**：抖音（快节奏强情绪）、视频号（熟人社交传播）、B站（深度内容社区）
- **结构化输出**：标题 + 节奏化文案 + 分镜建议 + 话题标签 + 发布时间建议
- **平台差异对比**：自动分析不同平台脚本的核心差异
- **多种输出格式**：JSON（机器消费） + Markdown（人阅读）
- **飞书集成**（可选）：一键发布到飞书文档 + 机器人通知
- **Web界面 + CLI**：Streamlit 可视化界面 + 命令行工具

## 系统架构

```
用户(Web UI/CLI) → Workflow引擎 → LLM(创意解析→平台脚本生成→差异对比)
                                       ↓
                                  飞书文档归档(可选)
                                       ↓
                                  飞书机器人通知(可选)
```

## 目录结构

```
cross-platform-video-agent/
├── app.py                    # Streamlit Web 入口
├── cli.py                    # CLI 命令行入口
├── requirements.txt          # Python 依赖
├── config/
│   ├── platform_rules.json   # 三平台规则参数配置
│   ├── llm_config.json       # LLM API 配置
│   └── feishu_config.json    # 飞书凭证（可选）
├── src/
│   ├── agent/                # 智能体核心
│   │   ├── workflow.py       # 主工作流编排
│   │   ├── prompts.py        # Prompt 提示词模板
│   │   └── parser.py         # JSON 解析 & 重试
│   ├── platforms/            # 平台适配层
│   │   ├── base.py           # 平台规则数据模型
│   │   ├── douyin.py         # 抖音适配器
│   │   ├── shipinhao.py      # 视频号适配器
│   │   └── bilibili.py       # B站适配器
│   ├── llm/                  # LLM 调用层
│   │   └── client.py         # OpenAI 兼容客户端
│   ├── feishu/               # 飞书集成（可选）
│   │   └── publisher.py      # 文档发布 & 机器人推送
│   └── utils/                # 工具层
│       ├── config_loader.py  # 配置文件加载
│       ├── validator.py      # 输入校验
│       └── reporter.py       # JSON/MD 报告生成
└── tests/                    # 测试
    ├── test_validator.py
    ├── test_parser.py
    ├── test_reporter.py
    ├── test_config.py
    └── test_prompts.py
```

## 快速开始

### 环境要求

- Python 3.7+
- DeepSeek API Key（或其他 OpenAI 兼容 API）

### 安装

```bash
# 克隆仓库
git clone <your-repo-url>
cd cross-platform-video-agent

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. **LLM 配置**：编辑 `config/llm_config.json`

```json
{
  "provider": "deepseek",
  "api_base": "https://api.deepseek.com/v1",
  "api_key": "sk-your-api-key-here",
  "model": "deepseek-chat",
  "max_tokens": 4096,
  "temperature": 0.8
}
```

2. **飞书配置**（可选）：编辑 `config/feishu_config.json`

```json
{
  "enabled": false,
  "app_id": "cli_xxxxxxxx",
  "app_secret": "xxxxxxxx",
  "bot_webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
}
```

### 使用方式

#### Web 界面

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501`，在界面中：
1. 输入创作主题或上传脚本草稿
2. 勾选目标平台（抖音/视频号/B站）
3. 点击"生成多平台脚本"
4. 在 Tab 页查看各平台脚本和差异对比
5. 下载 JSON/Markdown 报告

#### CLI 命令

```bash
# 查看帮助
python cli.py --help

# 查看当前配置
python cli.py config

# 查看平台规则
python cli.py rules --platform douyin

# 生成脚本（JSON + Markdown）
python cli.py generate -i "夏日防晒误区科普" -p douyin -p bilibili -o report

# 生成脚本并发布到飞书
python cli.py generate -i "夏日防晒误区科普" -p douyin -p shipinhao --feishu
```

### 运行测试

```bash
pytest tests/ -v
```

## 平台规则配置

平台规则定义在 `config/platform_rules.json`，支持自定义修改：

| 参数 | 抖音 | 视频号 | B站 |
|------|------|--------|-----|
| 最佳时长 | 45秒 | 90秒 | 5分钟 |
| 标题风格 | 悬念反问+标签 | 经验分享型 | 【硬核科普】前缀 |
| 内容调性 | 快节奏、强情绪 | 真实感、信任感 | 深度、专业、数据支撑 |
| 互动方式 | 引导关注+预告 | 引导转发收藏 | 弹幕互动+一键三连 |
| 发布时间 | 12:00/20:00 | 7:00/12:00/21:00 | 周五晚/周末 |

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Streamlit |
| 后端 | Python 3.7+ |
| LLM | DeepSeek API（OpenAI 兼容） |
| CLI | Click |
| 飞书 | lark-oapi |
| 测试 | pytest |

## License

MIT