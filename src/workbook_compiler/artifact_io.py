"""Shared artifact input/output helpers for the ECCS Workbook Compiler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load JSON content from an artifact file."""

    if not path.exists():
        raise FileNotFoundError(
            f"Artifact file not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def write_json(
    data: Any,
    output_file: Path,
) -> None:
    """Write JSON data to an ECCS artifact file."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
