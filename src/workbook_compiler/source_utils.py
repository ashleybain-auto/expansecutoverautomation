"""Shared source-text utilities for the ECCS Workbook Compiler."""

from __future__ import annotations


def line_number_at(
    source: str,
    position: int,
) -> int:
    """Return the one-based line number for a character position."""

    return (
        source.count(
            "\n",
            0,
            position,
        )
        + 1
    )
