from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from typing import Optional

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.validator import validate_input, CLARIFICATION_QUESTIONS
from src.utils.reporter import generate_json_report, generate_markdown_report


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """跨平台短视频脚本适配与优化智能体 CLI"""


@cli.command()
@click.option("--input", "-i", "content", required=True, help="创作主题或脚本草稿文本")
@click.option(
    "--platforms",
    "-p",
    multiple=True,
    default=["douyin", "shipinhao"],
    help="目标平台: douyin, shipinhao, bilibili",
)
@click.option("--tone", "-t", default=None, help="内容调性")
@click.option("--audience", "-a", default=None, help="目标受众")
@click.option("--output", "-o", default=None, help="输出文件路径（不含扩展名）")
@click.option("--format", "-f", "output_format", default="both", type=click.Choice(["json", "md", "both"]), help="输出格式")
@click.option("--feishu", is_flag=True, help="发布到飞书")
def generate(
    content: str,
    platforms: tuple[str, ...],
    tone: Optional[str],
    audience: Optional[str],
    output: Optional[str],
    output_format: str,
    feishu: bool,
):
    """生成多平台短视频脚本"""
    target_platforms = list(platforms)

    validation = validate_input(
        content=content,
        target_platforms=target_platforms,
        options={"tone": tone, "target_audience": audience},
    )

    if not validation.is_valid:
        click.echo(f"[ERROR] {validation.message}", err=True)
        if validation.needs_clarification:
            click.echo("请补充以下信息：", err=True)
            for q in CLARIFICATION_QUESTIONS:
                click.echo(f"  - {q}", err=True)
        sys.exit(1)

    click.echo(f"输入类型: {validation.input_type}")
    click.echo(f"目标平台: {', '.join(target_platforms)}")
    click.echo("正在生成...")

    from src.agent.workflow import run_workflow

    try:
        result = run_workflow(
            content=validation.content,
            target_platforms=target_platforms,
            options={"tone": tone, "target_audience": audience} if tone or audience else {},
        )
        click.echo(f"生成完成！任务ID: {result['task_id']}")
    except Exception as e:
        click.echo(f"[ERROR] 生成失败: {e}", err=True)
        sys.exit(1)

    base_name = output or f"video_script_{result['task_id'][:8]}"

    if output_format in ("json", "both"):
        json_path = f"{base_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(generate_json_report(result))
        click.echo(f"JSON 报告已保存: {json_path}")

    if output_format in ("md", "both"):
        md_path = f"{base_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(generate_markdown_report(result))
        click.echo(f"Markdown 报告已保存: {md_path}")

    if feishu:
        from src.feishu.publisher import publish_to_feishu

        click.echo("正在发布到飞书...")
        title = result.get("creative_analysis", {}).get("core_theme", "短视频脚本")
        md_report = generate_markdown_report(result)
        feishu_result = publish_to_feishu(title, md_report)
        click.echo(f"飞书发布结果: {json.dumps(feishu_result, ensure_ascii=False)}")


@cli.command()
@click.option("--platform", "-p", default="douyin", help="平台名称: douyin, shipinhao, bilibili")
def rules(platform: str):
    """查看平台规则配置"""
    from src.utils.config_loader import load_platform_rules

    rules = load_platform_rules()
    if platform not in rules:
        click.echo(f"不支持的平台: {platform}", err=True)
        click.echo(f"支持的平台: {', '.join(rules.keys())}")
        sys.exit(1)

    from src.platforms.base import PlatformRule
    rule = PlatformRule.from_dict(rules[platform])
    click.echo(rule.to_prompt_context())


@cli.command()
def config():
    """查看当前配置状态"""
    from src.utils.config_loader import load_llm_config, load_feishu_config

    llm = load_llm_config()
    click.echo("=== LLM 配置 ===")
    click.echo(f"Provider: {llm.get('provider')}")
    click.echo(f"Model: {llm.get('model')}")
    click.echo(f"API Base: {llm.get('api_base')}")
    api_key = llm.get("api_key", "")
    click.echo(f"API Key: {'已配置' if api_key and 'YOUR_' not in api_key else '未配置'}")

    feishu = load_feishu_config()
    click.echo("")
    click.echo("=== 飞书配置 ===")
    click.echo(f"启用状态: {'已启用' if feishu.get('enabled') else '未启用'}")
    app_id = feishu.get("app_id", "")
    click.echo(f"App ID: {'已配置' if app_id and 'YOUR_' not in app_id else '未配置'}")


if __name__ == "__main__":
    cli()