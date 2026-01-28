"""WebSocket broadcaster for real-time updates.

"Radical Visibility" - If an agent acts, the Frontend MUST know.
"""
import json
from datetime import datetime
from typing import Any
from src.websocket.manager import connection_manager


def serialize_for_json(obj: Any) -> Any:
    """Serialize objects for JSON, handling datetime."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


async def broadcast_agent_update(agent) -> None:
    """Broadcast agent state change to all connected clients."""
    message = {
        "type": "AGENT_UPDATE",
        "payload": {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role.value if hasattr(agent.role, 'value') else agent.role,
            "status": agent.status.value if hasattr(agent.status, 'value') else agent.status,
            "current_task": agent.current_task,
            "current_action": agent.current_action,
            "tokens_used_today": agent.tokens_used_today,
            "updated_at": serialize_for_json(agent.updated_at),
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    await connection_manager.broadcast(json.dumps(message))


async def broadcast_task_update(task) -> None:
    """Broadcast task state change to all connected clients."""
    message = {
        "type": "TASK_UPDATE",
        "payload": {
            "id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "status": task.status.value if hasattr(task.status, 'value') else task.status,
            "assigned_agent_id": task.assigned_agent_id,
            "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
            "updated_at": serialize_for_json(task.updated_at),
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    await connection_manager.broadcast(json.dumps(message))


async def broadcast_runplan_update(runplan) -> None:
    """Broadcast RunPlan state change to all connected clients."""
    message = {
        "type": "RUNPLAN_UPDATE",
        "payload": {
            "id": runplan.id,
            "task_id": runplan.task_id,
            "skill_name": runplan.skill_name,
            "status": runplan.status.value if hasattr(runplan.status, 'value') else runplan.status,
            "current_step": runplan.current_step,
            "total_steps": runplan.total_steps,
            "tokens_used": runplan.tokens_used,
            "updated_at": serialize_for_json(runplan.updated_at),
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    await connection_manager.broadcast(json.dumps(message))


async def broadcast_audit_event(audit_log) -> None:
    """Broadcast audit event to all connected clients."""
    message = {
        "type": "AUDIT_EVENT",
        "payload": {
            "id": audit_log.id,
            "action": audit_log.action.value if hasattr(audit_log.action, 'value') else audit_log.action,
            "description": audit_log.description,
            "agent_id": audit_log.agent_id,
            "success": audit_log.success,
            "created_at": serialize_for_json(audit_log.created_at),
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    await connection_manager.broadcast(json.dumps(message))
