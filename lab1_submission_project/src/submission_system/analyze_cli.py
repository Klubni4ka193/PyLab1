import argparse
import json
from pathlib import Path
from dataclasses import asdict

from submission_system.analyzer_service import AnalysisService, AnalyzerRegistry
from submission_system.analyzers import BasicContext, LengthAnalyzer, TemplateAnalyzer
from submission_system.sources import JsonlSubmissionSource


def main() -> None:
    parser = argparse.ArgumentParser(description="Запуск простых анализаторов")
    parser.add_argument("submissions", help="Путь к JSONL с корректными сдачами")
    parser.add_argument("assignments", help="Путь к assignments.json")
    args = parser.parse_args()

    assignments = json.loads(Path(args.assignments).read_text(encoding="utf-8"))
    registry = AnalyzerRegistry()
    registry.register("length", LengthAnalyzer)
    registry.register("template", TemplateAnalyzer)
    service = AnalysisService(registry)

    reports = []
    
    with JsonlSubmissionSource(args.submissions) as source:
        for submission in source.load():
            assignment = assignments.get(submission.assignment_id, {})
            context = BasicContext(
                assignment_id=submission.assignment_id,
                allowed_templates=assignment.get("allowed_templates", []),
            )
            for analyzer_id in ("length", "template"):
                reports.append({
                    "submission_id": submission.submission_id,
                    "report": asdict(service.analyze(analyzer_id, submission, context)),
                })
                
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
