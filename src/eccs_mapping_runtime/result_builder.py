"""ECCS mapping result construction."""

from __future__ import annotations

from typing import Any


def build_mapping_result(
    source_row: dict[str, Any],
    candidate: dict[str, Any] | None,
) -> dict[str, Any]:
    """Create the normalized ECCS mapping result record."""
    if candidate is None:
        return {
            "SourceRowId": source_row.get("SourceRowId", ""),
            "Status": "No Match",
            "Score": 0,
            "Grade": "Primary",
            "TargetFound": False,
            "RequiresReview": True,
            "RequiresApproval": True,
        }

    score = float(candidate.get("score", 0))
    grade = str(candidate.get("grade", "Primary"))

    return {
        "SourceRowId": source_row.get("SourceRowId", ""),
        "Status": "Candidate",
        "Score": score,
        "Grade": grade,
        "TargetFound": True,
        "TargetRank": candidate.get("rank", 1),
        "Target": candidate.get("target"),
        "MatchedFields": candidate.get(
            "matchedFields",
            [],
        ),
        "RequiresReview": True,
        "RequiresApproval": True,
    }
    
