# Лабораторная работа 1 — приём работ и расширяемые анализаторы

## Требования

- Python 3.10 или новее
- `pip`
- Для тестов: `pytest`

## Установка

Откройте терминал в корне проекта и выполните:

```bash
python -m venv .venv
```

Активация окружения:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows cmd**
```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Установка проекта и тестовых зависимостей:

```bash
python -m pip install -e ".[dev]"
```

## Формат сдачи

Одна строка `submissions.jsonl` — один JSON-объект. Пример:

```json
{"submission_id":"sub-001","student_id":"student-001","assignment_id":"lab-1","submitted_at":"2026-10-17T09:30:00+03:00","text":"Решение задачи","code":"print('hello')","ai_declaration":{"used":false,"details":""}}
```

Обязательные поля: `submission_id`, `student_id`, `assignment_id`, `submitted_at`, `text`, `code`, `ai_declaration`. Неизвестные поля запрещены. `submitted_at` должен включать часовой пояс. Если `ai_declaration.used` равен `true`, поле `details` должно быть непустым.

## Запуск импорта

```bash
lab1-import data/submissions.jsonl
```

Либо без установки команды:

```bash
python -m submission_system.cli data/submissions.jsonl
```

Команда печатает JSON с массивами `accepted`, `duplicate` и `errors`. Ошибка в одной строке не прерывает импорт всего файла.

## Запуск анализаторов

```bash
python -m submission_system.analyze_cli data/submissions.jsonl data/assignments.json
```

`LengthAnalyzer` считает непустые строки текста и кода. `TemplateAnalyzer` ищет точные совпадения строк с разрешёнными шаблонами, переданными через `assignments.json`. Совпадение помечается как разрешённое, а не как доказательство списывания.

Пример `assignments.json`:

```json
{
  "lab-1": {
    "allowed_templates": ["# TODO: implement", "def main():"]
  }
}
```

## Тесты

```bash
pytest
```

## Структура

```text
lab1_submission_project/
├── pyproject.toml
├── README.md
├── AI_USAGE.md
├── .gitignore
├── data/
│   ├── submissions.jsonl
│   ├── invalid_submissions.jsonl
│   └── assignments.json
├── src/
│   └── submission_system/
│       ├── __init__.py
│       ├── models.py
│       ├── validation.py
│       ├── repository.py
│       ├── service.py
│       ├── sources.py
│       ├── analyzers.py
│       ├── analyzer_service.py
│       ├── cli.py
│       └── analyze_cli.py
└── tests/
    ├── test_validation_and_import.py
    └── test_analyzers.py
```

## Публикация на GitHub

1. Создайте пустой репозиторий на GitHub.
2. В терминале в папке проекта выполните:

```bash
git init
git add .
git commit -m "stage-a"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/ВАШ_РЕПОЗИТОРИЙ.git
git push -u origin main
```

3. После завершения обеих частей можно сделать итоговый коммит с сообщением `lab-1`.

Перед публикацией проверьте, что в репозитории нет паролей, токенов и реальных работ студентов.
