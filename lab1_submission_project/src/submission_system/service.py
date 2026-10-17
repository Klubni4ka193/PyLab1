from submission_system.models import Submission
from submission_system.repository import InMemorySubmissionRepository, StoreResult
from submission_system.validation import parse_submission_json


class SubmissionService:
    """Доменный сервис: валидирует данные и сохраняет их в репозитории."""

    def __init__(self, repository: InMemorySubmissionRepository) -> None:
        self.repository = repository

    def import_json(self, raw: str) -> StoreResult:
        submission: Submission = parse_submission_json(raw)
        return self.repository.add(submission)
