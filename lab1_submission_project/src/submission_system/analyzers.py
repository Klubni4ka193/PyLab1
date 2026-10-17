from typing import Protocol

from submission_system.models import AnalysisReport, Submission


class AnalyzerContext(Protocol):
    assignment_id: str
    allowed_templates: list[str]


class Analyzer(Protocol):
    analyzer_id: str
    analyzer_version: str

    def analyze(self, submission: Submission, context: AnalyzerContext) -> AnalysisReport:
        """Анализирует сдачу и возвращает стандартный отчёт."""


class BasicContext:
    def __init__(self, assignment_id: str, allowed_templates: list[str] | None = None) -> None:
        self.assignment_id = assignment_id
        self.allowed_templates = allowed_templates or []


class LengthAnalyzer:
    analyzer_id = "length"
    analyzer_version = "1.0"

    def analyze(self, submission: Submission, context: AnalyzerContext) -> AnalysisReport:
        text_lines = sum(1 for line in submission.text.splitlines() if line.strip())
        code_lines = sum(1 for line in submission.code.splitlines() if line.strip())
        feedback = [
            f"Непустых строк текста: {text_lines}.",
            f"Непустых строк кода: {code_lines}.",
        ]
        return AnalysisReport(
            analyzer_id=self.analyzer_id,
            analyzer_version=self.analyzer_version,
            rubric_feedback=feedback,
            score=None,
            evidence=[],
        )


class TemplateAnalyzer:
    analyzer_id = "template"
    analyzer_version = "1.0"

    def analyze(self, submission: Submission, context: AnalyzerContext) -> AnalysisReport:
        allowed = set(context.allowed_templates)
        evidence: list[dict[str, object]] = []
        for section_name, content in (("text", submission.text), ("code", submission.code)):
            for line_number, line in enumerate(content.splitlines(), start=1):
                if line in allowed:
                    evidence.append({
                        "field": section_name,
                        "line": line_number,
                        "matched_text": line,
                        "explanation": "Точное совпадение с разрешённым шаблоном.",
                    })
        feedback = [
            f"Найдено совпадений с разрешёнными шаблонами: {len(evidence)}.",
            "Совпадение с разрешённым шаблоном само по себе не означает нарушение.",
        ]
        return AnalysisReport(
            analyzer_id=self.analyzer_id,
            analyzer_version=self.analyzer_version,
            rubric_feedback=feedback,
            score=None,
            similarity=1.0 if evidence else 0.0,
            evidence=evidence,
        )
