"""
Routes for querying Celery task results.
"""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_active_user
from app.models import User
from celery.result import AsyncResult

from celery_app import celery_app

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get(
    "/{task_id}",
    summary="Get the status and result of a Celery task",
)
def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Return the current state and (if finished) result of a Celery task.
    """
    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "state": result.state,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
    }

    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = str(result.result)
    else:
        # Include progress info if provided via meta
        response["info"] = result.info if isinstance(result.info, dict) else None

    return response
