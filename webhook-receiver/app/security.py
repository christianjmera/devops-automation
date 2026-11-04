import hashlib
import hmac

from app import config


def verify_signature(payload: bytes, signature: str | None) -> bool:
    if not signature:
        return False

    expected_signature = "sha256=" + hmac.new(
        config.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)
