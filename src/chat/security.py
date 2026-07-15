import hmac

from src.config import settings


def verify_token(token: str) -> bool:
    """
    Mattermost sends the slash command's configured verification token
    with every request. Compare it against our configured secret using a
    constant-time comparison to avoid leaking timing information.

    Note: Mattermost's slash command payload has no timestamp/nonce field,
    so replay protection isn't possible at this layer — rely on HTTPS and
    treat the token purely as an authenticity check, not a one-time secret.
    """
    if not token or not settings.mattermost_token:
        return False
    return hmac.compare_digest(token, settings.mattermost_token)