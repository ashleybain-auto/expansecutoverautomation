"""ECCS Source-to-Expanse weighted mapping engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class MatchWeights:
    """Weighted contribution of each matching field."""

    facility: float = 30.0
    mnemonic: float = 30.0
    name_description: float = 20.0
    secondary_key: float = 10.0
    active: float = 10.0


@dataclass(frozen=True)
class MatchResult:
    """Calculated mapping score and ECCS match grade."""

    score: float
    grade: str
    matched_fields: tuple[str, ...]


def normalize(value: Any) -> str:
    """Normalize source and target values for comparison."""
    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .upper()
        .split(),
    )


def field_matches(source: Any, target: Any) -> bool:
    """Return True when normalized source and target values match."""
    source_value = normalize(source)
    target_value = normalize(target)

    if not source_value or not target_value:
        return False

    return source_value == target_value


def grade_for_score(score: float) -> str:
    """Convert a 0-100 score into the ECCS configured match grade."""
    if score < 0 or score > 100:
        raise ValueError("Match score must be between 0 and 100.")

    if score <= 25:
        return "Primary"

    if score <= 50:
        return "Secondary"

    if score <= 75:
        return "Tertiary"

    return "Complete"


def calculate_match_score(
    source_row: dict[str, Any],
    target_row: dict[str, Any],
    weights: MatchWeights | None = None,
) -> MatchResult:
    """Calculate the ECCS weighted source-to-target match."""
    weights = weights or MatchWeights()

    field_definitions = [
        ("Facility", "facility", weights.facility),
        ("Mnemonic", "mnemonic", weights.mnemonic),
        ("NameDescription", "name_description", weights.name_description),
        ("PASecondaryKey", "secondary_key", weights.secondary_key),
        ("Active", "active", weights.active),
    ]

    score = 0.0
    matched_fields: list[str] = []

    for field_name, _, weight in field_definitions:
        if field_matches(
            source_row.get(field_name),
            target_row.get(field_name),
        ):
            score += weight
            matched_fields.append(field_name)

    score = round(score, 2)

    return MatchResult(
        score=score,
        grade=grade_for_score(score),
        matched_fields=tuple(matched_fields),
    )


def rank_candidates(
    source_row: dict[str, Any],
    target_rows: Iterable[dict[str, Any]],
    weights: MatchWeights | None = None,
) -> list[dict[str, Any]]:
    """Score and rank Expanse target candidates for a source row."""
    ranked: list[dict[str, Any]] = []

    for target_row in target_rows:
        result = calculate_match_score(
            source_row,
            target_row,
            weights,
        )

        ranked.append(
            {
                "target": target_row,
                "score": result.score,
                "grade": result.grade,
                "matchedFields": list(result.matched_fields),
            }
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return ranked
