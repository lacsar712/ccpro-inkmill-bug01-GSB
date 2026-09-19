from datetime import datetime

from flask import jsonify


def error(message: str, status: int = 400):
    return jsonify({"message": message}), status


def normalize_datetime(value: str) -> datetime:
    value = (value or "").strip()
    if not value:
        return datetime.now()
    cleaned = value.replace("Z", "").replace("z", "")
    if "+" in cleaned[10:]:
        cleaned = cleaned[: cleaned.index("+", 10)]
    cleaned = cleaned.strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(cleaned[:26], fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return datetime.now()


def dt_to_json(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
