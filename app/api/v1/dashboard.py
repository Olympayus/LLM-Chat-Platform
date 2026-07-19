"""Dashboard API (F-DB) — Member F"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.response import success

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/user")
async def user_dashboard(db: AsyncSession = Depends(get_db)):
    """User console: quick links, recent chats, unread count, stats cards"""
    return success(data={
        "quick_links": [
            {"name": "IM Chat", "path": "/im", "icon": "ChatDotRound"},
            {"name": "NL2SQL", "path": "/nl2sql", "icon": "DataAnalysis"},
            {"name": "Files", "path": "/files", "icon": "Folder"},
        ],
        "recent_conversations": [],
        "unread_messages": 0,
        "unread_notifications": 0,
        "stats": {"today_messages": 0, "today_queries": 0},
    })


@router.get("/admin")
async def admin_dashboard(db: AsyncSession = Depends(get_db)):
    """Admin console: system overview, trend charts, crawler stats"""
    return success(data={
        "total_users": 0,
        "today_active": 0,
        "current_online": 0,
        "today_messages": 0,
        "message_trend": [],
        "crawler_stats": {"today_tasks": 0, "success_rate": 0},
        "model_calls": 0,
        "storage_used_mb": 0,
        "storage_total_mb": 1024,
    })


@router.get("/user/recent")
async def user_recent(db: AsyncSession = Depends(get_db)):
    """Recent sessions and quick actions"""
    return success(data={"recent_conversations": [], "pending_tasks": []})


@router.get("/admin/stats")
async def admin_stats(db: AsyncSession = Depends(get_db)):
    """Detailed system statistics"""
    return success(data={
        "users": {"total": 0, "active_today": 0, "online": 0},
        "messages": {"today": 0, "week": [0]*7, "month": [0]*30},
        "crawler": {"total_tasks": 0, "running": 0, "success_rate": 0},
        "models": {"total_calls": 0, "avg_latency_ms": 0},
        "storage": {"used_mb": 0, "total_mb": 1024},
    })
