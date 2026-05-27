from __future__ import annotations

import json
import logging
from typing import Any
from pathlib import Path

logger = logging.getLogger(__name__)


class FeishuPublisher:
    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = str(
                Path(__file__).resolve().parent.parent.parent / "config" / "feishu_config.json"
            )
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    @property
    def is_enabled(self) -> bool:
        return bool(self.config.get("enabled", False))

    def create_document(self, title: str, markdown_content: str) -> dict[str, Any]:
        if not self.is_enabled:
            logger.warning("飞书集成未启用，跳过文档创建")
            return {"status": "skipped", "reason": "飞书集成未启用"}

        try:
            import lark_oapi as lark
            from lark_oapi.api.docx.v1 import (
                CreateDocumentRequest,
                CreateDocumentRequestBody,
            )

            client = lark.Client.builder() \
                .app_id(self.config["app_id"]) \
                .app_secret(self.config["app_secret"]) \
                .build()

            request = CreateDocumentRequest(
                request_body=CreateDocumentRequestBody(
                    title=title,
                    folder_token=self.config.get("folder_token") or "",
                )
            )
            response = client.docx.v1.document.create(request)
            if not response.success():
                logger.error("飞书文档创建失败: %s", response.msg)
                return {"status": "error", "message": f"创建失败: {response.msg}"}

            doc_id = response.data.document.document_id
            doc_url = f"https://bytedance.feishu.cn/docx/{doc_id}"

            self._write_document_content(client, doc_id, markdown_content)

            return {
                "status": "success",
                "document_id": doc_id,
                "url": doc_url,
            }
        except ImportError:
            logger.error("lark-oapi 未安装，请执行 pip install lark-oapi")
            return {"status": "error", "message": "lark-oapi 未安装"}
        except Exception as e:
            logger.error("飞书文档创建异常: %s", e)
            return {"status": "error", "message": str(e)}

    def _write_document_content(self, client, doc_id: str, markdown_content: str):
        try:
            import lark_oapi as lark
            from lark_oapi.api.docx.v1 import (
                UpdateDocumentBlockRequest,
                UpdateDocumentBlockRequestBody,
                Block,
                Text,
                TextElement,
            )

            blocks = self._md_to_blocks(markdown_content)
            for i, block in enumerate(blocks):
                request = UpdateDocumentBlockRequest(
                    document_id=doc_id,
                    block_id=doc_id,
                    request_body=UpdateDocumentBlockRequestBody(
                        update_text_elements=block,
                    ),
                )
                client.docx.v1.document_block.update(request)
        except Exception as e:
            logger.warning("飞书文档内容写入失败: %s", e)

    def _md_to_blocks(self, content: str) -> list:
        return [content[:5000]]

    def send_bot_message(self, title: str, doc_url: str) -> dict[str, Any]:
        if not self.is_enabled:
            logger.warning("飞书集成未启用，跳过机器人通知")
            return {"status": "skipped", "reason": "飞书集成未启用"}

        webhook_url = self.config.get("bot_webhook_url", "")
        if not webhook_url or webhook_url.startswith("YOUR_"):
            logger.warning("飞书机器人 Webhook URL 未配置")
            return {"status": "skipped", "reason": "Webhook URL 未配置"}

        try:
            import requests

            message = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {"tag": "plain_text", "content": "短视频脚本已生成"},
                        "template": "blue",
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**{title}**\n\n多平台脚本已生成完毕，点击下方链接查看详细报告。",
                            },
                        },
                        {
                            "tag": "action",
                            "actions": [
                                {
                                    "tag": "button",
                                    "text": {"tag": "plain_text", "content": "查看飞书文档"},
                                    "type": "primary",
                                    "url": doc_url,
                                }
                            ],
                        },
                    ],
                },
            }

            resp = requests.post(webhook_url, json=message, timeout=10)
            if resp.status_code == 200:
                return {"status": "success", "message": "消息推送成功"}
            return {"status": "error", "message": f"推送失败: {resp.text}"}
        except ImportError:
            logger.error("requests 未安装")
            return {"status": "error", "message": "requests 未安装"}
        except Exception as e:
            logger.error("飞书机器人推送异常: %s", e)
            return {"status": "error", "message": str(e)}


def publish_to_feishu(title: str, markdown_report: str) -> dict[str, Any]:
    publisher = FeishuPublisher()
    if not publisher.is_enabled:
        return {"document": {"status": "skipped"}, "bot": {"status": "skipped"}}

    doc_result = publisher.create_document(title, markdown_report)
    bot_result = {"status": "skipped"}
    if doc_result.get("status") == "success":
        bot_result = publisher.send_bot_message(title, doc_result.get("url", ""))
    return {"document": doc_result, "bot": bot_result}