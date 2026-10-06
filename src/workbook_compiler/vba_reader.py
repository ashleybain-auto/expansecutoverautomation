"""Static VBA extraction utilities for the ECCS Workbook Compiler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from oletools.olevba import VBA_Parser


def extract_modules(
    parser: VBA_Parser,
) -> list[dict[str, Any]]:
    """Extract VBA modules from an initialized parser."""

    modules: list[dict[str, Any]] = []

    for (
        filename,
        stream_path,
        vba_filename,
        vba_code,
    ) in parser.extract_macros():

        modules.append(
            {
                "filename": filename,
                "stream_path": stream_path,
                "vba_filename": vba_filename,
                "source": vba_code,
            }
        )

    return modules


def extract_analysis(
    parser: VBA_Parser,
) -> list[dict[str, str]]:
    """Extract VBA analysis findings."""

    analysis: list[dict[str, str]] = []

    for (
        result_type,
        keyword,
        description,
    ) in (parser.analyze_macros() or ()):

        analysis.append(
            {
                "type": str(result_type),
                "keyword": str(keyword),
                "description": str(description),
            }
        )

    return analysis


def write_vba_artifacts(
    output_dir: Path,
    modules: list[dict[str, Any]],
    analysis: list[dict[str, str]],
) -> tuple[Path, Path, Path]:
    """Write extracted VBA source, modules, and analysis artifacts."""

    source_parts: list[str] = []

    for module in modules:
        source_parts.append(
            f"===== {module['vba_filename']} ====="
        )

        source_parts.append(
            f"Source: {module['filename']}"
        )

        source_parts.append(
            f"Stream: {module['stream_path']}"
        )

        source_parts.append(
            str(module["source"])
        )

    source_file = (
        output_dir / "vba-source.txt"
    )

    source_file.write_text(
        "\n\n".join(source_parts),
        encoding="utf-8",
    )

    modules_file = (
        output_dir / "vba-modules.json"
    )

    modules_file.write_text(
        json.dumps(
            modules,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    analysis_file = (
        output_dir / "vba-analysis.json"
    )

    analysis_file.write_text(
        json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return (
        source_file,
        modules_file,
        analysis_file,
    )


def extract_vba(
    workbook_path: str,
    output_dir: str,
) -> dict[str, Any]:
    """Extract VBA source and analysis without executing macros."""

    source = Path(workbook_path)
    destination = Path(output_dir)

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    parser = VBA_Parser(
        str(source)
    )

    try:
        has_vba = parser.detect_vba_macros()

        modules: list[dict[str, Any]] = []

        if has_vba:
            modules = extract_modules(
                parser
            )

        analysis: list[dict[str, str]] = []

        if has_vba:
            analysis = extract_analysis(
                parser
            )

        (
            source_file,
            modules_file,
            analysis_file,
        ) = write_vba_artifacts(
            destination,
            modules,
            analysis,
        )

        return {
            "workbook": str(source),
            "has_vba": has_vba,
            "module_count": len(modules),
            "analysis_count": len(analysis),
            "source_file": str(source_file),
            "modules_file": str(modules_file),
            "analysis_file": str(analysis_file),
        }

    finally:
        parser.close()
