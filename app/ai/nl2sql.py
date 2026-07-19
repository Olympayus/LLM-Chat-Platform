"""NL2SQL 智能问数引擎

核心功能:
1. build_system_prompt()  — 构建 System Prompt（含 Schema 信息）
2. build_few_shot_examples() — Few-shot 示例
3. read_schema()          — 从 information_schema 读取表结构
4. generate_sql()         — 调用 LLM 生成 SQL
5. recommend_chart()      — 根据数据推荐图表类型
6. interpret_results()    — AI 数据解读
"""

import json
import re
from typing import Any, Optional

from loguru import logger

from app.ai.client import LLMClient
from app.config import settings
from app.schemas.nl2sql import ChartRecommendation, ColumnInfo, TableSchema

# ==================== System Prompt ====================

SYSTEM_PROMPT_TEMPLATE = """你是一个专业的 NL2SQL 助手。请根据用户的问题和数据库 Schema，生成对应的 SQL 查询语句。

## 数据库 Schema

数据库名称: {database_name}

{table_schemas}

## 规则要求

1. **仅生成 SELECT 查询** — 不允许 INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, EXEC, CALL 等操作
2. **必须添加 LIMIT 子句** — 如果用户没有指定数量，默认 LIMIT 100
3. **禁止危险操作** — 禁止使用 INTO OUTFILE, LOAD_FILE, BENCHMARK, SLEEP 等函数
4. **使用标准 SQL** — 兼容 MySQL 5.7 语法
5. **列名引用** — 列名使用反引号 `` 括起来
6. **字符串比较** — 使用 LIKE 或 =，注意大小写兼容
7. **日期处理** — 使用 DATE_FORMAT, DATE_ADD, DATEDIFF 等 MySQL 函数
8. **聚合查询** — 使用 GROUP BY 时，SELECT 中的非聚合列必须出现在 GROUP BY 中
9. **表别名** — 多表 JOIN 时使用简短的表别名

## 输出格式

你**必须**只返回纯 SQL 语句，不要包含任何解释、注释或 Markdown 代码块标记。
只返回 SQL 本身，例如:
SELECT * FROM sys_user LIMIT 10

## 注意事项

- 如果问题不明确，做出合理的假设并生成 SQL
- 如果问题无法用 SQL 回答，返回: -- ERROR: 无法将问题转换为 SQL 查询，原因: ...
- 如果需要查询表结构信息（如有哪些表、字段），请查询 information_schema
"""

# ==================== Few-shot Examples ====================

FEW_SHOT_EXAMPLES = [
    {
        "question": "查询所有用户的用户名和邮箱",
        "sql": "SELECT `username`, `email` FROM `sys_user` LIMIT 100",
    },
    {
        "question": "统计各部门的人数",
        "sql": "SELECT d.`name` AS `部门名称`, COUNT(u.`id`) AS `人数` FROM `sys_dept` d LEFT JOIN `sys_user` u ON d.`id` = u.`dept_id` GROUP BY d.`id`, d.`name` ORDER BY `人数` DESC",
    },
    {
        "question": "查询最近7天创建的模型配置",
        "sql": "SELECT `id`, `display_name`, `model_id`, `created_at` FROM `model_config` WHERE `created_at` >= DATE_SUB(NOW(), INTERVAL 7 DAY) ORDER BY `created_at` DESC LIMIT 50",
    },
    {
        "question": "查找包含'测试'关键字的技能",
        "sql": "SELECT `id`, `name`, `type`, `description` FROM `skill` WHERE `name` LIKE '%测试%' OR `description` LIKE '%测试%' LIMIT 50",
    },
    {
        "question": "查询每个部门的部门名称和负责人ID",
        "sql": "SELECT `id`, `name`, `leader_id` FROM `sys_dept` WHERE `is_deleted` = 0 ORDER BY `sort_order` ASC LIMIT 100",
    },
]


class Nl2sqlEngine:
    """NL2SQL 引擎"""

    def __init__(self, llm: Optional[LLMClient] = None):
        """初始化 NL2SQL 引擎

        Args:
            llm: LLM 客户端实例。为 None 时使用默认配置创建实例。
        """
        if llm is not None:
            self.llm = llm
        else:
            self.llm = LLMClient(
                base_url=settings.DASHSCOPE_BASE_URL,
                api_key=settings.DASHSCOPE_API_KEY,
                model_id="qwen-plus",
            )

    # ==================== Prompt 工程 ====================

    def build_system_prompt(
        self,
        tables: list[TableSchema],
        database_name: str = "llm_platform",
    ) -> str:
        """构建 System Prompt"""
        table_schemas_str = self._format_schemas(tables)
        return SYSTEM_PROMPT_TEMPLATE.format(
            database_name=database_name,
            table_schemas=table_schemas_str,
        )

    def build_few_shot_messages(self) -> list[dict]:
        """构建 Few-shot 示例消息"""
        messages = []
        for example in FEW_SHOT_EXAMPLES:
            messages.append({"role": "user", "content": example["question"]})
            messages.append({"role": "assistant", "content": example["sql"]})
        return messages

    def _format_schemas(self, tables: list[TableSchema]) -> str:
        """将 Schema 结构格式化为文本"""
        lines = []
        for table in tables:
            lines.append(f"### 表: {table.table_name}")
            if table.table_comment:
                lines.append(f"注释: {table.table_comment}")
            lines.append("| 列名 | 类型 | 可为空 | 主键 | 注释 |")
            lines.append("|------|------|--------|------|------|")
            for col in table.columns:
                pk = "是" if col.is_primary_key else ""
                nullable = "是" if col.nullable else "否"
                comment = col.comment or ""
                lines.append(f"| {col.name} | {col.type} | {nullable} | {pk} | {comment} |")
            lines.append("")
        return "\n".join(lines)

    # ==================== Schema 读取 ====================

    async def read_schema(
        self,
        db_session: Any,
        database_name: str = "llm_platform",
    ) -> list[TableSchema]:
        """从 information_schema 读取数据库表结构

        Args:
            db_session: 数据库会话（异步 SQLAlchemy session）
            database_name: 数据库名

        Returns:
            list[TableSchema]: 表结构列表
        """
        # 注意: 此处需要真实的数据库连接。
        # 在没有数据库时返回 mock 数据。
        if db_session is None:
            return self._get_mock_schema()

        try:
            # 查询所有表
            tables_result = await db_session.execute(
                """
                SELECT TABLE_NAME, TABLE_COMMENT
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = :db AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
                """,
                {"db": database_name},
            )
            table_rows = tables_result.fetchall()

            tables = []
            for table_row in table_rows:
                table_name = table_row[0]
                table_comment = table_row[1] or ""

                # 查询表的列信息
                columns_result = await db_session.execute(
                    """
                    SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE,
                           COLUMN_COMMENT, COLUMN_KEY
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table
                    ORDER BY ORDINAL_POSITION
                    """,
                    {"db": database_name, "table": table_name},
                )
                column_rows = columns_result.fetchall()

                columns = [
                    ColumnInfo(
                        name=row[0],
                        type=row[1],
                        nullable=row[2] == "YES",
                        comment=row[3] or "",
                        is_primary_key=row[4] == "PRI",
                    )
                    for row in column_rows
                ]

                tables.append(
                    TableSchema(
                        table_name=table_name,
                        table_comment=table_comment,
                        columns=columns,
                    )
                )

            return tables

        except Exception as e:
            logger.error(f"读取数据库 Schema 失败: {e}")
            # 降级返回 mock 数据
            return self._get_mock_schema()

    def _get_mock_schema(self) -> list[TableSchema]:
        """获取 Mock Schema（无数据库时使用）"""
        return [
            TableSchema(
                table_name="sys_user",
                table_comment="用户表",
                columns=[
                    ColumnInfo(name="id", type="bigint unsigned", nullable=False, comment="用户ID", is_primary_key=True),
                    ColumnInfo(name="username", type="varchar(64)", nullable=False, comment="用户名"),
                    ColumnInfo(name="email", type="varchar(128)", nullable=True, comment="邮箱"),
                    ColumnInfo(name="mobile", type="varchar(20)", nullable=True, comment="手机号"),
                    ColumnInfo(name="real_name", type="varchar(64)", nullable=True, comment="真实姓名"),
                    ColumnInfo(name="dept_id", type="bigint unsigned", nullable=True, comment="所属部门"),
                    ColumnInfo(name="status", type="tinyint", nullable=False, comment="状态: 1=正常 0=禁用"),
                    ColumnInfo(name="created_at", type="datetime", nullable=False, comment="创建时间"),
                ],
            ),
            TableSchema(
                table_name="sys_dept",
                table_comment="部门表",
                columns=[
                    ColumnInfo(name="id", type="bigint unsigned", nullable=False, comment="部门ID", is_primary_key=True),
                    ColumnInfo(name="parent_id", type="bigint unsigned", nullable=False, comment="父部门ID"),
                    ColumnInfo(name="name", type="varchar(64)", nullable=False, comment="部门名称"),
                    ColumnInfo(name="leader_id", type="bigint unsigned", nullable=True, comment="负责人ID"),
                    ColumnInfo(name="sort_order", type="int", nullable=False, comment="排序"),
                    ColumnInfo(name="created_at", type="datetime", nullable=False, comment="创建时间"),
                ],
            ),
            TableSchema(
                table_name="model_config",
                table_comment="AI模型配置表",
                columns=[
                    ColumnInfo(name="id", type="bigint unsigned", nullable=False, comment="ID", is_primary_key=True),
                    ColumnInfo(name="display_name", type="varchar(128)", nullable=False, comment="展示名称"),
                    ColumnInfo(name="category", type="varchar(32)", nullable=False, comment="分类"),
                    ColumnInfo(name="model_id", type="varchar(128)", nullable=False, comment="模型ID"),
                    ColumnInfo(name="is_enabled", type="tinyint", nullable=False, comment="是否启用"),
                    ColumnInfo(name="created_at", type="datetime", nullable=False, comment="创建时间"),
                ],
            ),
            TableSchema(
                table_name="skill",
                table_comment="技能表",
                columns=[
                    ColumnInfo(name="id", type="bigint unsigned", nullable=False, comment="ID", is_primary_key=True),
                    ColumnInfo(name="name", type="varchar(128)", nullable=False, comment="技能名称"),
                    ColumnInfo(name="type", type="varchar(32)", nullable=False, comment="类型"),
                    ColumnInfo(name="description", type="text", nullable=False, comment="技能描述"),
                    ColumnInfo(name="is_enabled", type="tinyint", nullable=False, comment="是否启用"),
                    ColumnInfo(name="created_by", type="bigint unsigned", nullable=True, comment="创建者"),
                ],
            ),
            TableSchema(
                table_name="digital_employee",
                table_comment="数字员工表",
                columns=[
                    ColumnInfo(name="id", type="bigint unsigned", nullable=False, comment="ID", is_primary_key=True),
                    ColumnInfo(name="name", type="varchar(64)", nullable=False, comment="员工名称"),
                    ColumnInfo(name="model_id", type="bigint unsigned", nullable=False, comment="绑定模型ID"),
                    ColumnInfo(name="is_enabled", type="tinyint", nullable=False, comment="是否启用"),
                    ColumnInfo(name="system_prompt", type="text", nullable=False, comment="系统提示词"),
                ],
            ),
            TableSchema(
                table_name="im_group",
                table_comment="群组表",
                columns=[
                    ColumnInfo(name="id", type="bigint unsigned", nullable=False, comment="ID", is_primary_key=True),
                    ColumnInfo(name="group_name", type="varchar(128)", nullable=False, comment="群名称"),
                    ColumnInfo(name="owner_id", type="bigint unsigned", nullable=False, comment="群主ID"),
                    ColumnInfo(name="member_count", type="int unsigned", nullable=False, comment="成员数"),
                    ColumnInfo(name="status", type="tinyint", nullable=False, comment="1=正常 0=已解散"),
                ],
            ),
            TableSchema(
                table_name="im_message",
                table_comment="消息表",
                columns=[
                    ColumnInfo(name="id", type="bigint unsigned", nullable=False, comment="ID", is_primary_key=True),
                    ColumnInfo(name="chat_type", type="varchar(16)", nullable=False, comment="private/group"),
                    ColumnInfo(name="sender_id", type="bigint unsigned", nullable=False, comment="发送者ID"),
                    ColumnInfo(name="content", type="text", nullable=False, comment="消息内容"),
                    ColumnInfo(name="msg_type", type="varchar(16)", nullable=False, comment="消息类型"),
                    ColumnInfo(name="created_at", type="datetime", nullable=False, comment="创建时间"),
                ],
            ),
        ]

    # ==================== SQL 生成 ====================

    async def generate_sql(
        self,
        question: str,
        tables: Optional[list[TableSchema]] = None,
        database_name: str = "llm_platform",
        db_session: Any = None,
    ) -> str:
        """根据自然语言问题生成 SQL

        Args:
            question: 自然语言问题
            tables: 表结构列表，如果为 None 则从数据库读取
            database_name: 数据库名
            db_session: 数据库会话

        Returns:
            str: 生成的 SQL 语句
        """
        # 获取 Schema
        if tables is None:
            tables = await self.read_schema(db_session, database_name)

        # 构建消息
        system_prompt = self.build_system_prompt(tables, database_name)
        few_shot_msgs = self.build_few_shot_messages()

        messages = [
            {"role": "system", "content": system_prompt},
            *few_shot_msgs,
            {"role": "user", "content": question},
        ]

        try:
            response = await self.llm.chat(
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
            )
            sql = response.choices[0].message.content if response.choices else ""

            # 清理输出：移除 markdown 代码块标记
            sql = self._clean_sql_output(sql)
            return sql

        except Exception as e:
            logger.error(f"SQL 生成失败: {e}")
            return f"-- ERROR: SQL 生成失败 - {str(e)}"

    def _clean_sql_output(self, raw_sql: str) -> str:
        """清理 LLM 返回的 SQL 文本"""
        # 移除 ```sql ... ``` 或 ``` ... ``` 代码块
        sql = re.sub(r"```(?:sql)?\s*\n?(.*?)\n?```", r"\1", raw_sql, flags=re.DOTALL)
        # 移除首尾空白
        sql = sql.strip()
        # 如果有多条 SQL，只取第一条
        sql = sql.split(";")[0].strip()
        return sql

    # ==================== 图表推荐 ====================

    def recommend_chart(
        self,
        columns: list[str],
        rows: list[list[Any]],
        question: str,
    ) -> ChartRecommendation:
        """根据查询结果推荐图表类型"""
        if not columns or not rows:
            return ChartRecommendation(
                chart_type="table",
                title="查询结果",
                reasoning="无数据返回，推荐使用表格展示",
            )

        col_count = len(columns)
        row_count = len(rows)

        # 简单启发式规则：
        # 1. 如果只有1列 → 表格
        if col_count == 1:
            return ChartRecommendation(
                chart_type="table",
                title=columns[0],
                reasoning="单列数据，推荐使用表格展示",
            )

        # 2. 如果有2列，且第2列是数值 → 柱状图
        if col_count >= 2:
            try:
                second_col_values = [row[1] for row in rows if row[1] is not None]
                if second_col_values and all(self._is_numeric(v) for v in second_col_values):
                    # 检查是否是时间序列（第1列包含日期关键词或值看起来像日期）
                    first_col_name = columns[0].lower()
                    is_time_series = any(
                        kw in first_col_name for kw in ["date", "time", "年", "月", "日", "created_at", "updated_at"]
                    )

                    if is_time_series and len(rows) > 3:
                        return ChartRecommendation(
                            chart_type="line",
                            title=f"{columns[0]} 与 {columns[1]} 的关系",
                            x_axis=columns[0],
                            y_axis=[columns[1]],
                            reasoning="检测到时间序列数据，推荐使用折线图展示趋势",
                        )

                    # 检查是否适合饼图（类别少于10个）
                    first_col_values = [row[0] for row in rows if row[0] is not None]
                    unique_categories = len(set(str(v) for v in first_col_values))
                    if unique_categories <= 10 and unique_categories >= 2:
                        return ChartRecommendation(
                            chart_type="pie",
                            title=f"{columns[1]} 分布",
                            x_axis=columns[0],
                            y_axis=[columns[1]],
                            reasoning=f"检测到 {unique_categories} 个分类，推荐使用饼图展示占比",
                        )

                    return ChartRecommendation(
                        chart_type="bar",
                        title=f"{columns[0]} 的 {columns[1]}",
                        x_axis=columns[0],
                        y_axis=[columns[1]],
                        reasoning="包含数值列，推荐使用柱状图对比",
                    )
            except (IndexError, TypeError):
                pass

        # 3. 多列复杂数据 → 表格
        return ChartRecommendation(
            chart_type="table",
            title=f"查询结果 (共 {row_count} 行)",
            reasoning=f"多列复杂数据 ({col_count}列 {row_count}行)，推荐使用表格展示",
        )

    def _is_numeric(self, value: Any) -> bool:
        """判断值是否为数值类型"""
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        return False

    # ==================== AI 数据解读 ====================

    async def interpret_results(
        self,
        question: str,
        sql: str,
        columns: list[str],
        rows: list[list[Any]],
        llm: Optional[LLMClient] = None,
    ) -> str:
        """使用 AI 解读查询结果

        Args:
            question: 用户原始问题
            sql: 执行的 SQL
            columns: 结果列名
            rows: 结果数据行
            llm: LLM 客户端

        Returns:
            str: 数据解读文本
        """
        if not rows:
            return "查询未返回数据。"

        _llm = llm or self.llm

        # 构建数据摘要
        summary = self._build_result_summary(columns, rows)

        prompt = f"""你是一个数据分析师。请根据用户的问题、SQL 查询和数据结果，给出简洁的数据解读。

用户问题: {question}

SQL 查询:
{sql}

查询结果摘要:
{summary}

请给出数据解读（3-5句话），包括:
1. 数据概况（总行数、关键指标）
2. 数据中发现的模式或趋势
3. 有价值的业务洞察
4. 如果有异常值，指出异常

注意: 保持专业、客观，不要编造不存在的数据。"""

        try:
            response = await _llm.chat(
                messages=[
                    {"role": "system", "content": "你是一个专业的数据分析师，请根据查询结果给出简洁的数据解读。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            interpretation = response.choices[0].message.content if response.choices else ""
            return interpretation.strip()
        except Exception as e:
            logger.error(f"数据解读失败: {e}")
            return f"查询返回 {len(rows)} 行数据，共 {len(columns)} 列。"

    def _build_result_summary(self, columns: list[str], rows: list[list[Any]]) -> str:
        """构建查询结果摘要"""
        if not rows:
            return "无数据"

        line = f"总行数: {len(rows)}, 列数: {len(columns)}\n"
        line += f"列名: {', '.join(columns)}\n\n"

        # 显示前5行数据
        line += "前5行数据:\n"
        line += " | ".join(columns) + "\n"
        line += "-" * 50 + "\n"
        for row in rows[:5]:
            line += " | ".join(str(v) if v is not None else "NULL" for v in row) + "\n"

        # 数值列统计
        line += "\n数值列统计:\n"
        for i, col in enumerate(columns):
            numeric_values = []
            for row in rows:
                try:
                    val = row[i]
                    if val is not None:
                        numeric_values.append(float(val))
                except (ValueError, TypeError, IndexError):
                    pass

            if numeric_values:
                line += f"- {col}: 最小值={min(numeric_values):.2f}, 最大值={max(numeric_values):.2f}, "
                line += f"平均值={sum(numeric_values) / len(numeric_values):.2f}\n"

        return line


# 全局单例
nl2sql_engine = Nl2sqlEngine()