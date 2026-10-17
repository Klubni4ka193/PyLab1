import argparse
import json
from pathlib import Path
from typing import Any

from submission_system.repository import InMemorySubmissionRepository
from submission_system.service import SubmissionService
from submission_system.validation import SubmissionInputError


def import_file(path: str | Path) -> dict[str, Any]:
    repository = InMemorySubmissionRepository()
    service = SubmissionService(repository)
    report: dict[str, Any] = {"accepted": [], "duplicate": [], "errors": []}

    with Path(path).open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                result = service.import_json(line)
                if result.status == "accepted":
                    report["accepted"].append({
                        "line": line_number,
                        "submission_id": result.submission.submission_id,
                    })
                elif result.status == "duplicate":
                    report["duplicate"].append({
                        "line": line_number,
                        "submission_id": result.submission.submission_id,
                    })
                else:
                    report["errors"].append({
                        "line": line_number,
                        "code": "id_conflict",
                        "field": "submission_id",
                        "message": "submission_id уже использован для другого содержимого",
                    })
            except SubmissionInputError as exc:
                error = exc.error
                report["errors"].append({
                    "line": line_number,
                    "code": error.code,
                    "field": error.field,
                    "message": error.message,
                })
    report["total_stored"] = len(repository)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Импорт сдач из JSONL")
    parser.add_argument("file", help="Путь к JSONL-файлу")
    args = parser.parse_args()
    try:
        result = import_file(args.file)
    except OSError as exc:
        parser.error(f"Не удалось открыть файл: {exc}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
