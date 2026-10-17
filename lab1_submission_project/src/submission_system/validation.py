import json
from datetime import datetime
from typing import Any

from submission_system.models import AIDeclaration, Submission, ValidationError


ALLOWED_FIELDS = {
    "submission_id", "student_id", "assignment_id", "submitted_at",
    "text", "code", "ai_declaration",
}


class SubmissionInputError(Exception):
    """Ошибка входных данных с понятным кодом, полем и сообщением."""

    def __init__(self, code: str, field: str, message: str) -> None:
        super().__init__(message)
        self.error = ValidationError(code=code, field=field, message=message)


def parse_submission_json(raw: str) -> Submission:
    """Разбирает JSON и проверяет схему, не меняя исходную строку."""
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SubmissionInputError("invalid_json", "$", f"Некорректный JSON: {exc.msg}") from exc

    if not isinstance(data, dict):
        raise SubmissionInputError("invalid_schema", "$", "Ожидался JSON-объект")

    unknown = set(data) - ALLOWED_FIELDS
    if unknown:
        field = sorted(unknown)[0]
        raise SubmissionInputError("unknown_field", field, "Неизвестное поле")

    missing = ALLOWED_FIELDS - set(data)
    if missing:
        field = sorted(missing)[0]
        raise SubmissionInputError("missing_field", field, "Обязательное поле отсутствует")

    for field in ("submission_id", "student_id", "assignment_id", "text", "code"):
        value = data[field]
        if not isinstance(value, str):
            raise SubmissionInputError("invalid_type", field, "Ожидалась строка")
        if field in ("submission_id", "student_id", "assignment_id") and not value.strip():
            raise SubmissionInputError("empty_field", field, "Поле не должно быть пустым")

    timestamp = data["submitted_at"]
    if not isinstance(timestamp, str):
        raise SubmissionInputError("invalid_type", "submitted_at", "Ожидалась строка даты и времени")
    try:
        parsed_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SubmissionInputError("invalid_timestamp", "submitted_at", "Неверный формат даты и времени") from exc
    if parsed_time.tzinfo is None or parsed_time.utcoffset() is None:
        raise SubmissionInputError("missing_timezone", "submitted_at", "Укажите часовой пояс, например +03:00 или Z")

    declaration = data["ai_declaration"]
    if not isinstance(declaration, dict):
        raise SubmissionInputError("invalid_type", "ai_declaration", "Ожидался объект")
    if set(declaration) != {"used", "details"}:
        raise SubmissionInputError("invalid_schema", "ai_declaration", "Ожидаются только поля used и details")
    if not isinstance(declaration["used"], bool):
        raise SubmissionInputError("invalid_type", "ai_declaration.used", "Ожидалось true или false")
    if not isinstance(declaration["details"], str):
        raise SubmissionInputError("invalid_type", "ai_declaration.details", "Ожидалась строка")
    if declaration["used"] and not declaration["details"].strip():
        raise SubmissionInputError("missing_ai_details", "ai_declaration.details",
                                   "Если used=true, details не должно быть пустым")

    return Submission(
        submission_id=data["submission_id"],
        student_id=data["student_id"],
        assignment_id=data["assignment_id"],
        submitted_at=parsed_time,
        text=data["text"],
        code=data["code"],
        ai_declaration=AIDeclaration(
            used=declaration["used"],
            details=declaration["details"],
        ),
    )
