from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class AIDeclaration:
    used: bool
    details: str


@dataclass(frozen=True)
class Submission:
    submission_id: str
    student_id: str
    assignment_id: str
    submitted_at: datetime
    text: str
    code: str
    ai_declaration: AIDeclaration


@dataclass(frozen=True)
class ValidationError:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class AnalysisReport:
    analyzer_id: str
    analyzer_version: str
    rubric_feedback: list[str]
    score: float | None = None
    similarity: float | None = None
    evidence: list[dict[str, Any]] | None = None
