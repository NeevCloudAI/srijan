import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.security import verify_token
from src.db.constants import CommandType, JobStatus
from src.db.models import Job
from src.db.session import get_db
from src.logging import get_logger
from src.workers.tasks import process_job

router = APIRouter()
logger = get_logger(__name__)
_executor = ThreadPoolExecutor(max_workers=2)

ACK_MESSAGE = "Working on it! I'll update this thread shortly."


@router.post("/webhook/dev")
async def handle_dev_command(request: Request, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Receives /neevai-dev slash commands from Mattermost."""
    return await _handle_command(request, db, command_type=CommandType.DEV)


@router.post("/webhook/debug")
async def handle_debug_command(request: Request, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Receives /neevai-debug slash commands from Mattermost."""
    return await _handle_command(request, db, command_type=CommandType.DEBUG)


async def _handle_command(request: Request, db: AsyncSession, command_type: CommandType) -> JSONResponse:
    form = await request.form()

    if not verify_token(form.get("token", "")):
        logger.warning(f"Rejected {command_type} webhook: invalid token")
        raise HTTPException(status_code=401, detail="Invalid verification token")

    user_id = form.get("user_id", "")
    channel_id = form.get("channel_id", "")
    task_text = form.get("text", "").strip()

    if not user_id or not channel_id:
        raise HTTPException(status_code=400, detail="Missing user_id or channel_id")

    job = Job(command_type=command_type, user_id=user_id, channel_id=channel_id, task_text=task_text)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Hand off to the background worker immediately — this request must
    # return within Mattermost's 3-second window. Use thread pool to avoid
    # blocking the async event loop with the Redis network call.
    loop = asyncio.get_event_loop()
    loop.run_in_executor(_executor, process_job.apply_async, [str(job.id)], {"queue": f"{command_type}-queue"})

    return JSONResponse(content={"response_type": "ephemeral", "text": ACK_MESSAGE})