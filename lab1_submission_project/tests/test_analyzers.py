import json

from submission_system.analyzer_service import AnalysisService, AnalyzerRegistry
from submission_system.analyzers import BasicContext, LengthAnalyzer, TemplateAnalyzer
from submission_system.validation import parse_submission_json


def make_submission():
    data = {
        "submission_id": "sub-1",
        "student_id": "student-1",
        "assignment_id": "lab-1",
        "submitted_at": "2026-10-17T09:30:00+03:00",
        "text": "hello\n\nworld",
        "code": "def main():\n    pass\n",
        "ai_declaration": {"used": False, "details": ""},
    }
    return parse_submission_json(json.dumps(data))


def test_length_analyzer_counts_nonempty_lines():
    report = LengthAnalyzer().analyze(make_submission(), BasicContext("lab-1"))
    assert report.analyzer_id == "length"
    assert report.score is None
    assert report.rubric_feedback == [
        "Непустых строк текста: 2.",
        "Непустых строк кода: 2.",
    ]


def test_template_analyzer_returns_original_line_numbers():
    report = TemplateAnalyzer().analyze(
        make_submission(),
        BasicContext("lab-1", ["def main():", "world"]),
    )
    assert report.similarity == 1.0
    assert report.evidence[0]["line"] == 3
    assert report.evidence[1]["line"] == 1


def test_registry_selects_analyzer():
    registry = AnalyzerRegistry()
    registry.register("length", LengthAnalyzer)
    service = AnalysisService(registry)
    report = service.analyze("length", make_submission(), BasicContext("lab-1"))
    assert report.analyzer_id == "length"


def test_registry_rejects_unknown_analyzer():
    registry = AnalyzerRegistry()
    service = AnalysisService(registry)
    try:
        service.analyze("missing", make_submission(), BasicContext("lab-1"))
        assert False, "Ожидалась ошибка"
    except ValueError as exc:
        assert "Неизвестный анализатор" in str(exc)
