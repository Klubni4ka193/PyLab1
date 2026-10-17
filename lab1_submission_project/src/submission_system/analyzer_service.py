from collections.abc import Callable

from submission_system.analyzers import Analyzer, AnalyzerContext
from submission_system.models import AnalysisReport, Submission


AnalyzerFactory = Callable[[], Analyzer]


class AnalyzerRegistry:

    def __init__(self) -> None:
        self._factories: dict[str, AnalyzerFactory] = {}

    def register(self, analyzer_id: str, factory: AnalyzerFactory) -> None:
        if analyzer_id in self._factories:
            raise ValueError(f"Анализатор {analyzer_id!r} уже зарегистрирован")
        self._factories[analyzer_id] = factory

    def create(self, analyzer_id: str) -> Analyzer:
        try:
            factory = self._factories[analyzer_id]
        except KeyError as exc:
            raise ValueError(f"Неизвестный анализатор: {analyzer_id}") from exc
        return factory()


class AnalysisService:
    def __init__(self, registry: AnalyzerRegistry) -> None:
        self.registry = registry

    def analyze(
        self, analyzer_id: str, submission: Submission, context: AnalyzerContext
    ) -> AnalysisReport:
        analyzer = self.registry.create(analyzer_id)
        return analyzer.analyze(submission, context)
