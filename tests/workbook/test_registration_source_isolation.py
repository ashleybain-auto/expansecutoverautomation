"""Regression tests for ECCS Registration source isolation."""

import json
from pathlib import Path


EXPANSE_MANIFEST = Path(
    "manifests/ECCS/REG/EXPANSE/"
    "migration-manifest.json"
)

NONMAGIC_MANIFEST = Path(
    "manifests/ECCS/REG/NONMAGIC/"
    "migration-manifest.json"
)


def load_manifest(path: Path) -> dict:
    """Load a migration manifest."""

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def test_registration_variants_use_distinct_sources() -> None:
    """Verify EXPANSE and NONMAGIC use separate source workbooks."""

    expanse = load_manifest(
        EXPANSE_MANIFEST
    )

    nonmagic = load_manifest(
        NONMAGIC_MANIFEST
    )

    assert (
        expanse["configTool"]["variant"]
        == "EXPANSE"
    )

    assert (
        nonmagic["configTool"]["variant"]
        == "NONMAGIC"
    )

    assert (
        expanse["source"]["workbook"]
        == "Mapping_Expanse_REG_Domain.xlsb"
    )

    assert (
        nonmagic["source"]["workbook"]
        == "Mapping_NonMagic_Expanse_REG_Domain.xlsb"
    )

    assert (
        expanse["source"]["sha256"]
        != nonmagic["source"]["sha256"]
    )
