from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    Returns 200 OK if the Srijan service is running.
    """
    return {"status": "ok", "service": "srijan"}