from dataclasses import dataclass
from hashlib import sha256

from submission_system.models import Submission


@dataclass(frozen=True)
class StoreResult:
    status: str  # accepted, duplicate, conflict
    submission: Submission | None = None


def submission_hash(submission: Submission) -> str:
    """Хеш содержимого сдачи, не включая идентификатор самой сдачи."""
    content = "\\0".join([
        submission.student_id,
        submission.assignment_id,
        submission.submitted_at.isoformat(),
        submission.text,
        submission.code,
        str(submission.ai_declaration.used),
        submission.ai_declaration.details,
    ])
    return sha256(content.encode("utf-8")).hexdigest()


class InMemorySubmissionRepository:
    def __init__(self) -> None:
        self._items: dict[str, tuple[str, Submission]] = {}

    def add(self, submission: Submission) -> StoreResult:
        digest = submission_hash(submission)
        existing = self._items.get(submission.submission_id)
        if existing:
            old_hash, old_submission = existing
            if old_hash == digest:
                return StoreResult("duplicate", old_submission)
            return StoreResult("conflict", old_submission)

        self._items[submission.submission_id] = (digest, submission)
        return StoreResult("accepted", submission)

    def get(self, submission_id: str) -> Submission | None:
        item = self._items.get(submission_id)
        return item[1] if item else None

    def __len__(self) -> int:
        return len(self._items)
