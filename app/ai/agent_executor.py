"""数字员工 Agent 执行引擎"""

import json
from typing import Any, Optional

from loguru import logger

from app.ai.client import LLMClient


class AgentExecutor:
    """数字员工 Agent 执行引擎 — LLM + Function Call 调度循环

    执行流程:
    1. 加载数字员工配置 (system_prompt + model + skills)
    2. 构建 messages = [system_prompt, ...chat_history, user_message]
    3. 构建 tools = [skill1.to_function(), skill2.to_function()]
    4. 调用 LLM (with tools)
       ├── LLM 返回 function_call → 提取参数
       │   └── 在沙箱中执行 python_code → 获取结果
       │   └── 将结果作为 function_result 追加到 messages
       │   └── 再次调用 LLM → 生成最终回复
       └── LLM 直接返回文本 → 返回回复
    """

    MAX_LOOP = 5  # 最大 Function Call 循环次数，防止无限循环

    def __init__(self, client: LLMClient, system_prompt: str, skills: Optional[list[dict]] = None):
        """
        Args:
            client: LLM 客户端实例
            system_prompt: 系统提示词
            skills: 绑定的技能列表 [{"name":..., "description":..., "params_schema":..., "python_code":...}]
        """
        self.client = client
        self.system_prompt = system_prompt
        self.skills = skills or []

    def _build_tools(self) -> Optional[list[dict[str, Any]]]:
        """将技能列表转换为 OpenAI Function Calling 的 tools 格式"""
        if not self.skills:
            return None

        tools = []
        for skill in self.skills:
            tool = {
                "type": "function",
                "function": {
                    "name": skill["name"],
                    "description": skill["description"],
                },
            }
            if skill.get("params_schema"):
                tool["function"]["parameters"] = skill["params_schema"]
            else:
                tool["function"]["parameters"] = {"type": "object", "properties": {}}

            tools.append(tool)

        return tools

    async def execute(
        self,
        user_message: str,
        chat_history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """执行 Agent 对话

        Args:
            user_message: 用户消息
            chat_history: 历史对话 [{"role": "user/assistant", "content": "..."}]

        Returns:
            dict: {"reply": str, "function_calls": [...]}
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # 追加历史对话
        if chat_history:
            messages.extend(chat_history)

        # 追加当前用户消息
        messages.append({"role": "user", "content": user_message})

        tools = self._build_tools()
        function_calls_log = []

        loop_count = 0
        while loop_count < self.MAX_LOOP:
            loop_count += 1

            try:
                response = await self.client.chat(
                    messages=messages,
                    tools=tools,
                    temperature=0.7,
                    max_tokens=4096,
                )
            except Exception as e:
                logger.error(f"Agent 调用 LLM 失败: {e}")
                return {
                    "reply": f"抱歉，AI 服务暂时不可用: {str(e)}",
                    "function_calls": function_calls_log,
                }

            choice = response.choices[0]
            message = choice.message

            # 检查是否有 function_call
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Agent 调用技能: {function_name}({function_args})")

                    # 查找对应技能的 Python 代码并执行
                    function_result = self._execute_skill(function_name, function_args)

                    function_calls_log.append({
                        "name": function_name,
                        "arguments": function_args,
                        "result": str(function_result),
                    })

                    # 追加 assistant 的 tool_calls 消息
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": tool_call.function.arguments,
                                },
                            }
                        ],
                    })

                    # 追加 function 执行结果
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(function_result),
                    })

                # 继续循环，让 LLM 处理 function 结果
                continue

            # 没有 function_call，直接返回文本
            reply = message.content or ""
            return {
                "reply": reply,
                "function_calls": function_calls_log,
            }

        # 超过最大循环次数
        logger.warning(f"Agent 达到最大循环次数 {self.MAX_LOOP}")
        return {
            "reply": "处理超时，请稍后重试。",
            "function_calls": function_calls_log,
        }

    def _execute_skill(self, function_name: str, arguments: dict) -> str:
        """执行技能 — 根据技能名称查找并执行 Python 代码

        注意：在实际生产环境中，Python 代码应在 Docker 沙箱中执行。
        这里提供简化的直接执行实现。
        """
        # 查找匹配的技能
        skill = None
        for s in self.skills:
            if s["name"] == function_name:
                skill = s
                break

        if not skill:
            return f"错误：未找到技能 {function_name}"

        python_code = skill.get("python_code")
        if not python_code:
            return f"错误：技能 {function_name} 没有可执行代码"

        try:
            # 在受限的命名空间中执行代码
            local_vars = {"params": arguments}
            exec(python_code, {"__builtins__": {}}, local_vars)

            # 查找 execute 函数并调用
            if "execute" in local_vars:
                result = local_vars["execute"](arguments)
                return str(result)
            else:
                return f"错误：技能 {function_name} 的代码中没有定义 execute(params) 函数"

        except Exception as e:
            logger.error(f"执行技能 {function_name} 失败: {e}")
            return f"技能执行错误: {str(e)}"