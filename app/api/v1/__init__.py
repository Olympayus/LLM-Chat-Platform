"""API v1 路由注册

包含:
- auth.py: 认证 + 用户/部门/角色/菜单管理（成员A）
- models_config.py: 模型管理（成员B）
- skills.py: 技能管理（成员B）
- digital_employees.py: 数字员工管理（成员B）
- nl2sql.py: NL2SQL 智能问数（成员E）
- compliance.py: 合规审计（成员D）
- crawlers.py: 爬虫管理与数据清洗（成员F）
- im.py: IM 即时通讯 REST API（成员C）
- websocket.py: IM WebSocket 端点（成员C）
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.models_config import router as models_router
from app.api.v1.nl2sql import router as nl2sql_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.skills import router as skills_router
from app.api.v1.digital_employees import router as digital_employees_router
from app.api.v1.crawlers import router as crawlers_router
from app.api.v1.im import router as im_router
from app.api.v1.websocket import router as ws_router
from app.api.v1.upload import router as upload_router
from app.api.v1.notification import router as notification_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.files import router as files_router
from app.api.v1.sys_config import router as sys_config_router
from app.api.v1.profile import router as profile_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(models_router)
v1_router.include_router(nl2sql_router)
v1_router.include_router(compliance_router)
v1_router.include_router(skills_router)
v1_router.include_router(digital_employees_router)
v1_router.include_router(crawlers_router)
v1_router.include_router(im_router)
v1_router.include_router(ws_router)
v1_router.include_router(upload_router)
v1_router.include_router(notification_router)
v1_router.include_router(dashboard_router)
v1_router.include_router(files_router)
v1_router.include_router(sys_config_router)
v1_router.include_router(profile_router)

# 别名，兼容不同的引用方式
router = v1_router

__all__ = ["v1_router", "router"]
