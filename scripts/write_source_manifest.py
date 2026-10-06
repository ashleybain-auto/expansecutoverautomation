"""Write source identity metadata for an ECCS workbook analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hash of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(
            lambda: stream.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    """Write source workbook identity metadata."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--workbook",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    workbook = Path(args.workbook)
    output = Path(args.output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "filename": workbook.name,
        "full_path": str(
            workbook.resolve()
        ),
        "extension": workbook.suffix.lower(),
        "size_bytes": workbook.stat().st_size,
        "sha256": sha256_file(workbook),
    }

    output.write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Source manifest written: {output}"
    )


if __name__ == "__main__":
    main()
