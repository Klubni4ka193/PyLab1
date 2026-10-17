import json

from submission_system.cli import import_file
from submission_system.repository import InMemorySubmissionRepository
from submission_system.service import SubmissionService
from submission_system.validation import SubmissionInputError, parse_submission_json


VALID = {
    "submission_id": "sub-1",
    "student_id": "student-1",
    "assignment_id": "lab-1",
    "submitted_at": "2026-10-17T09:30:00+03:00",
    "text": "hello",
    "code": "print('hello')",
    "ai_declaration": {"used": False, "details": ""},
}


def raw(data=VALID):
    return json.dumps(data)


def test_valid_submission_parses():
    submission = parse_submission_json(raw())
    assert submission.submission_id == "sub-1"
    assert submission.submitted_at.tzinfo is not None


def test_invalid_json_has_error_code():
    try:
        parse_submission_json("{bad")
        assert False, "Ожидалась ошибка"
    except SubmissionInputError as exc:
        assert exc.error.code == "invalid_json"


def test_timestamp_requires_timezone():
    data = dict(VALID, submitted_at="2026-10-17T09:30:00")
    try:
        parse_submission_json(raw(data))
        assert False, "Ожидалась ошибка"
    except SubmissionInputError as exc:
        assert exc.error.code == "missing_timezone"


def test_empty_student_id_is_rejected():
    data = dict(VALID, student_id=" ")
    try:
        parse_submission_json(raw(data))
        assert False, "Ожидалась ошибка"
    except SubmissionInputError as exc:
        assert exc.error.field == "student_id"


def test_unknown_field_is_rejected():
    data = dict(VALID, unexpected="value")
    try:
        parse_submission_json(raw(data))
        assert False, "Ожидалась ошибка"
    except SubmissionInputError as exc:
        assert exc.error.code == "unknown_field"


def test_duplicate_and_conflict():
    repo = InMemorySubmissionRepository()
    service = SubmissionService(repo)
    assert service.import_json(raw()).status == "accepted"
    assert service.import_json(raw()).status == "duplicate"
    changed = dict(VALID, text="different content")
    assert service.import_json(raw(changed)).status == "conflict"
    assert len(repo) == 1


def test_ai_details_required_when_used():
    data = dict(VALID, ai_declaration={"used": True, "details": " "})
    try:
        parse_submission_json(raw(data))
        assert False, "Ожидалась ошибка"
    except SubmissionInputError as exc:
        assert exc.error.code == "missing_ai_details"


def test_import_continues_after_bad_line(tmp_path):
    good = raw()
    path = tmp_path / "input.jsonl"
    path.write_text(good + "\n{bad\n", encoding="utf-8")
    result = import_file(path)
    assert len(result["accepted"]) == 1
    assert len(result["errors"]) == 1
    assert result["errors"][0]["line"] == 2
