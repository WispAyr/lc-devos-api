"""Build Phase workflow endpoints."""
import subprocess
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.project import Project
from src.schemas.build import BuildInitRequest, BuildInitResponse

router = APIRouter(prefix="/build", tags=["build"])


@router.post("/init", response_model=BuildInitResponse)
async def initialize_build(
    request: BuildInitRequest,
    db: AsyncSession = Depends(get_db)
):
    """Initialize the build phase for a project.

    This transitions a project from design to build phase by:
    1. Storing the finalized requirements and tech stack
    2. Optionally creating a GitHub repository
    3. Updating the project phase
    """
    # Get the project
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Store design decisions in project config
    config = project.config or {}
    config["design"] = {
        "requirements": [r.model_dump() for r in request.requirements],
        "tech_stack": [t.model_dump() for t in request.tech_stack],
        "notes": request.notes,
    }
    config["phase"] = "build"
    project.config = config

    github_url = None
    next_steps = []

    # Create GitHub repo if requested
    if request.create_github_repo and request.github_repo_name:
        try:
            repo_name = request.github_repo_name.lower().replace(" ", "-")

            # Use gh CLI to create repo
            result = subprocess.run(
                ["gh", "repo", "create", repo_name, "--private", "--confirm"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Extract URL from output or construct it
                github_url = f"https://github.com/{os.environ.get('GITHUB_USER', 'user')}/{repo_name}"
                project.github_repo_name = repo_name
                project.github_repo_url = github_url
                next_steps.append(f"Clone repository: git clone {github_url}")
            else:
                # If gh fails, continue without repo
                next_steps.append("GitHub repo creation skipped (gh CLI not configured)")

        except Exception as e:
            next_steps.append(f"GitHub repo creation skipped: {str(e)}")

    # Standard next steps
    next_steps.extend([
        "Create initial project structure",
        "Set up development environment",
        "Implement core features",
    ])

    await db.flush()

    return BuildInitResponse(
        success=True,
        project_id=request.project_id,
        phase="build",
        github_repo_url=github_url,
        message="Project transitioned to build phase successfully",
        next_steps=next_steps,
    )


@router.get("/status/{project_id}")
async def get_build_status(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get the current build status of a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    config = project.config or {}
    phase = config.get("phase", "design")
    design = config.get("design", {})

    return {
        "project_id": project_id,
        "phase": phase,
        "has_requirements": len(design.get("requirements", [])) > 0,
        "has_tech_stack": len(design.get("tech_stack", [])) > 0,
        "github_repo_url": project.github_repo_url,
    }
