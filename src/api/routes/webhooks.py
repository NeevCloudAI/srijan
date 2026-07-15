from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/webhook/dev")
async def handle_dev_command(request: Request) -> JSONResponse:
    """
    Receives /neevai-dev slash commands from the chat platform.
    Phase 2 will add: validation, DB save, Celery enqueue.
    """
    # Placeholder — Phase 2 will implement this fully
    return JSONResponse(
        content={"text": "Srijan is online. /dev handler coming in Phase 2."}
    )


@router.post("/webhook/debug")
async def handle_debug_command(request: Request) -> JSONResponse:
    """
    Receives /neevai-debug slash commands from the chat platform.
    Phase 2 will add: validation, DB save, Celery enqueue.
    """
    # Placeholder — Phase 2 will implement this fully
    return JSONResponse(
        content={"text": "Srijan is online. /debug handler coming in Phase 2."}
    )