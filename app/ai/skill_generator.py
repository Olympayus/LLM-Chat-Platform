"""AI 辅助技能生成引擎"""

import json
from typing import Any, Optional

from loguru import logger

from app.ai.client import LLMClient


class SkillGenerator:
    """AI 辅助技能生成器 — 调用 LLM 根据自然语言需求生成技能"""

    SYSTEM_PROMPT = """你是一个 AI 技能生成助手。根据用户的需求描述，生成一个完整的技能定义。

对于 function_call 类型的技能，你需要输出以下 JSON 格式：
{
  "name": "技能名称（英文，下划线分隔）",
  "description": "给 LLM 的 function description，描述这个函数的作用、何时调用、参数含义",
  "params_schema": {
    "type": "object",
    "properties": {
      "param1": {"type": "string", "description": "参数说明"},
      "param2": {"type": "number", "description": "参数说明"}
    },
    "required": ["param1"]
  },
  "python_code": "def execute(params):\\n    # 在沙箱中执行的 Python 代码\\n    pass"
}

对于 skill_md 类型的技能，你需要输出一份详细的 SKILL.md 格式的 Markdown 文档。

请严格按照 JSON 格式返回，不要包含任何额外的解释文字。"""

    def __init__(self, client: LLMClient):
        self.client = client

    async def generate_function_call_skill(self, requirement: str) -> dict[str, Any]:
        """根据需求生成 Function Call 类型的技能

        Args:
            requirement: 自然语言需求描述

        Returns:
            dict: {
                "name": str,
                "description": str,
                "params_schema": dict,
                "python_code": str
            }
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"请生成一个 function_call 类型的技能：{requirement}"},
        ]

        try:
            response = await self.client.chat(
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )

            content = response.choices[0].message.content
            result = json.loads(content)
            logger.info(f"AI 生成技能成功: {result.get('name', 'unknown')}")
            return result

        except json.JSONDecodeError as e:
            logger.warning(f"AI 返回内容非 JSON，尝试提取: {e}")
            content = response.choices[0].message.content
            # 尝试从 Markdown 代码块中提取 JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                try:
                    result = json.loads(json_str)
                    return result
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"AI 生成内容无法解析为 JSON: {content[:500]}")

        except Exception as e:
            logger.error(f"AI 生成技能失败: {e}")
            raise

    async def generate_skill_md(self, requirement: str) -> str:
        """根据需求生成 SKILL.md 类型的技能文档

        Args:
            requirement: 自然语言需求描述

        Returns:
            str: SKILL.md 格式的 Markdown 内容
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"请生成一个 skill_md 类型的技能文档（标准 SKILL.md 格式）：{requirement}"},
        ]

        try:
            response = await self.client.chat(
                messages=messages,
                temperature=0.5,
                max_tokens=4096,
            )

            content = response.choices[0].message.content
            logger.info("AI 生成 SKILL.md 文档成功")
            return content

        except Exception as e:
            logger.error(f"AI 生成 SKILL.md 失败: {e}")
            raise