"""API route modules."""
from src.routes.agents import router as agents_router
from src.routes.tasks import router as tasks_router
from src.routes.projects import router as projects_router
from src.routes.runplans import router as runplans_router
from src.routes.audit import router as audit_router
from src.routes.costs import router as costs_router
from src.routes.health import router as health_router
from src.routes.mcp import router as mcp_router
from src.routes.design import router as design_router
from src.routes.build import router as build_router

__all__ = [
    "agents_router",
    "tasks_router",
    "projects_router",
    "runplans_router",
    "audit_router",
    "costs_router",
    "health_router",
    "mcp_router",
    "design_router",
    "build_router",
]
