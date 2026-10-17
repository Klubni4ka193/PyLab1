import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol

from submission_system.models import Submission
from submission_system.validation import parse_submission_json


class SubmissionSource(Protocol):
    def load(self) -> list[Submission]:
        """Возвращает набор корректных сдач."""


class InMemorySubmissionSource:
    def __init__(self, submissions: list[Submission]) -> None:
        self._submissions = list(submissions)

    def load(self) -> list[Submission]:
        return list(self._submissions)


class JsonlSubmissionSource:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Submission]:
        submissions: list[Submission] = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    submissions.append(parse_submission_json(line))
        return submissions
