"""ECCS candidate generation for Source-to-Expanse mapping."""

from __future__ import annotations

from typing import Any, Iterable

from .matcher import MatchWeights, rank_candidates


def build_candidates(
    source_row: dict[str, Any],
    target_rows: Iterable[dict[str, Any]],
    weights: MatchWeights | None = None,
) -> list[dict[str, Any]]:
    """Generate ranked Expanse target candidates for one source row."""
    candidates = rank_candidates(
        source_row=source_row,
        target_rows=target_rows,
        weights=weights,
    )

    for rank, candidate in enumerate(
        candidates,
        start=1,
    ):
        candidate["rank"] = rank
        candidate["sourceRowId"] = source_row.get(
            "SourceRowId",
            "",
        )

    return candidates


def select_top_candidate(
    candidates: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the highest-scoring candidate."""
    if not candidates:
        return None

    return candidates[0]
