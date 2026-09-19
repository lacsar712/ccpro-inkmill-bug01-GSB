from datetime import datetime, timezone

from flask import jsonify

# All timestamps crossing the API or stored in the database use UTC.
# JSON carries an explicit trailing "Z"; DB columns hold naive UTC datetimes.


def error(message: str, status: int = 400):
    return jsonify({"message": message}), status


def utcnow() -> datetime:
    """Current time as a naive UTC datetime (the shape stored in DB columns)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def normalize_datetime(value: str) -> datetime:
    """Parse an ISO-8601 timestamp into a naive UTC datetime.

    - A trailing ``Z``/``z`` or an explicit offset (e.g. ``+08:00``) is
      honoured and converted to UTC.
    - A value without any offset is interpreted as UTC (the API contract).
    - An empty value means "now" (UTC); an unparseable value raises
      ``ValueError`` so the caller can reject it with HTTP 400.
    """
    text = (value or "").strip()
    if not text:
        return utcnow()

    iso = text[:-1] + "+00:00" if text[-1] in ("Z", "z") else text
    iso = iso.replace(" ", "T", 1)

    parsed: datetime | None = None
    try:
        parsed = datetime.fromisoformat(iso)
    except ValueError:
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ):
            try:
                parsed = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        raise ValueError(f"无法解析时间: {value!r}")

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    # Naive input is defined to already be UTC, so it is returned as-is.
    return parsed


def dt_to_json(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    # DB datetimes are naive UTC; label them explicitly as UTC. isoformat()
    # keeps fractional seconds when present, so read-back is lossless.
    return dt.isoformat() + "Z"
