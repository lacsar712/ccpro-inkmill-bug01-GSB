from datetime import datetime, timezone

from flask import jsonify


def error(message: str, status: int = 400):
    return jsonify({"message": message}), status


def normalize_datetime(value: str) -> datetime:
    """Parse an ISO-8601 timestamp into a naive UTC datetime.

    Single convention across the app: datetimes stored in the DB are UTC.
    Inputs with an explicit offset (Z or ±hh:mm) are converted to UTC;
    naive inputs are assumed to already be UTC. Empty or unparseable
    input falls back to the current UTC time.
    """
    value = (value or "").strip()
    if not value:
        return datetime.utcnow()
    cleaned = value.replace(" ", "T")
    if cleaned.endswith(("Z", "z")):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return datetime.utcnow()
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def dt_to_json(dt: datetime | None) -> str | None:
    """Serialize a stored (naive UTC) datetime as ISO-8601 with Z suffix."""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
