"""Build an ECCS domain/action matrix from a procedure inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_matrix(
    source_file: Path,
    output_file: Path,
) -> None:
    """Build a domain/action matrix from classified procedures."""

    if not source_file.exists():
        raise FileNotFoundError(
            f"Procedure inventory not found: {source_file}"
        )

    procedures = json.loads(
        source_file.read_text(
            encoding="utf-8"
        )
    )

    domains: dict[str, set[str]] = {}

    for procedure in procedures:
        name = procedure["name"]
        classification = procedure["classification"]

        if classification == "REFRESH":
            prefix = "RefreshData_"

        elif classification == "PUBLISH":
            prefix = "PushUpdates_"

        else:
            continue

        if not name.startswith(prefix):
            continue

        domain = name[len(prefix):].strip()

        if domain:
            domains.setdefault(
                domain,
                set(),
            ).add(classification)

    result = [
        {
            "domain": domain,
            "actions": sorted(actions),
        }
        for domain, actions in sorted(
            domains.items()
        )
    ]

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Domains discovered: {len(result)}"
    )

    for item in result:
        print(
            f"{item['domain']}: "
            f"{', '.join(item['actions'])}"
        )

    print(
        f"Output: {output_file}"
    )


def main() -> None:
    """Parse arguments and generate the requested domain matrix."""

    parser = argparse.ArgumentParser(
        description="Build an ECCS domain/action matrix."
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Path to procedures.json.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to domain-actions.json.",
    )

    args = parser.parse_args()

    build_matrix(
        Path(args.source),
        Path(args.output),
    )


if __name__ == "__main__":
    main()
