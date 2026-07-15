import httpx

from src.config import settings
from src.logging import get_logger

logger = get_logger(__name__)


class MattermostClient:
    """
    Thin async wrapper around the Mattermost bot REST API.
    Used to post acknowledgments, progress updates, and final results
    back into the channel/thread a command came from.
    """

    def __init__(self) -> None:
        self._base_url = settings.mattermost_base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {settings.mattermost_bot_token}"}

    async def post_message(self, channel_id: str, message: str, root_id: str | None = None) -> dict:
        """
        Posts `message` to `channel_id`. If `root_id` is given, the post is
        threaded under that post instead of starting a new thread.
        Returns the created post (includes its "id", useful as a future root_id).
        """
        payload = {"channel_id": channel_id, "message": message}
        if root_id:
            payload["root_id"] = root_id

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self._base_url}/api/v4/posts", json=payload, headers=self._headers
            )
        if response.is_error:
            logger.error(f"Mattermost post failed ({response.status_code}): {response.text}")
            response.raise_for_status()
        return response.json()