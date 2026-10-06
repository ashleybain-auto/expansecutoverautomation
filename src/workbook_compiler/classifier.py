"""Functional classification for extracted ECCS VBA procedures."""

from __future__ import annotations


CLASSIFICATION_RULES = (
    ("refreshdata_", "REFRESH"),
    ("pushupdates_", "PUBLISH"),
    ("copydata_", "STAGE"),
    ("validate", "VALIDATE"),
    ("export", "EXPORT"),
    ("setting", "CONFIGURE"),
)


def classify_procedure(name: str) -> str:
    """Classify a VBA procedure by its functional responsibility."""

    normalized = name.casefold()

    for prefix, classification in CLASSIFICATION_RULES:
        if normalized.startswith(prefix):
            return classification

    return "OTHER"
