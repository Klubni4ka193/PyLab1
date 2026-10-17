import json
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from submission_system.models import Submission
from submission_system.validation import parse_submission_json


class SubmissionSource(Protocol):
    def load(self) -> Iterator[Submission] | list[Submission]:
        """Возвращает набор корректных сдач."""


class InMemorySubmissionSource:
    def __init__(self, submissions: list[Submission]) -> None:
        self._submissions = list(submissions)

    def load(self) -> list[Submission]:
        return list(self._submissions)


class JsonlSubmissionSource:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._file = None

    def __enter__(self) -> "JsonlSubmissionSource":
        self._file = self.path.open("r", encoding="utf-8")
        return self

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any | None) -> None:
        if self._file:
            self._file.close()
            self._file = None

    def load(self) -> Iterator[Submission]:
        if self._file is None:
            raise RuntimeError("Источник данных не открыт. Используйте менеджер контекста 'with'.")
        
        for line in self._file:
            if line.strip():
                yield parse_submission_json(line)
