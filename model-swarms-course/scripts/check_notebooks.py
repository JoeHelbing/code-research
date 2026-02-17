from __future__ import annotations

import json
from pathlib import Path

NOTEBOOKS = sorted(Path(".").glob("*.ipynb"))


def main() -> int:
    failures: list[str] = []
    for notebook in NOTEBOOKS:
        try:
            payload = json.loads(notebook.read_text())
        except json.JSONDecodeError as exc:
            failures.append(f"{notebook}: invalid JSON ({exc})")
            continue

        if "cells" not in payload:
            failures.append(f"{notebook}: missing top-level 'cells'")

    import_checks = {
        "module_03_lora_and_merging.ipynb": "from model_swarms_course.merging import",
        "module_04_algorithm_deep_dive.ipynb": (
        "from model_swarms_course.pso import model_swarms_velocity_update"
    ),
        "exercises.ipynb": "from model_swarms_course.merging import",
    }

    for notebook, needle in import_checks.items():
        content = Path(notebook).read_text()
        if needle not in content:
            failures.append(f"{notebook}: expected shared src import not found")

    if failures:
        print("Notebook checks failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"Notebook checks passed for {len(NOTEBOOKS)} notebook(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
