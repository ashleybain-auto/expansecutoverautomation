"""ECCS bulk-upload Source-to-Expanse mapping pipeline."""

from __future__ import annotations

from typing import Any, Iterable

from .candidate_mapping import build_candidates, select_top_candidate
from .csv_mapping import read_upload_csv
from .matcher import MatchWeights
from .result_builder import build_mapping_result


def process_upload(
    csv_path: str,
    target_rows: Iterable[dict[str, Any]],
    weights: MatchWeights | None = None,
) -> list[dict[str, Any]]:
    """Process an ECCS upload into mapping results."""
    source_rows = read_upload_csv(csv_path)

    results: list[dict[str, Any]] = []

    target_rows_list = list(target_rows)

    for source_row in source_rows:
        candidates = build_candidates(
            source_row=source_row,
            target_rows=target_rows_list,
            weights=weights,
        )

        top_candidate = select_top_candidate(
            candidates,
        )

        result = build_mapping_result(
            source_row=source_row,
            candidate=top_candidate,
        )

        result["CandidateCount"] = len(candidates)

        results.append(result)

    return results
