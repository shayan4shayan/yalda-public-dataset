#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import quote


# Base URL for hosting (fill this later).
# Examples:
# - GitHub raw:   https://raw.githubusercontent.com/<user>/<repo>/<branch>/
# - GitHub pages: https://<user>.github.io/<repo>/
# - Any CDN or server where these files will be hosted
BASE_URL = ""


def ensure_trailing_slash(url: str) -> str:
    return url if not url or url.endswith("/") else url + "/"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an index of JSON files with their URLs.")
    parser.add_argument(
        "--base-url",
        dest="base_url",
        default=None,
        help="Optional base URL to prefix each relative path. Overrides BASE_URL in the script if provided.",
    )
    parser.add_argument(
        "--output",
        dest="output",
        default="files.index.json",
        help="Output index file path (default: files.index.json)",
    )
    parser.add_argument(
        "--root",
        dest="root",
        default=None,
        help="Root directory to scan (default: repository root where this script resides)",
    )

    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = (
        Path(args.root).resolve() if args.root else script_path.parent.parent.resolve()
    )

    base_url = ensure_trailing_slash(args.base_url if args.base_url is not None else BASE_URL)

    # Collect all JSON files recursively under repo_root
    json_files: list[Path] = [
        p for p in repo_root.rglob("*.json")
        if p.is_file()
    ]

    # Exclude the output index file itself if inside the tree
    out_path = (repo_root / args.output).resolve()
    json_files = [p for p in json_files if p.resolve() != out_path]

    entries = []
    for p in json_files:
        rel = p.relative_to(repo_root).as_posix()

        # Build address: if base_url provided, prefix it; otherwise use the relative path
        address = (base_url + quote(rel)) if base_url else rel

        entries.append({
            "name": p.name,
            "address": address,
        })

    # Stable ordering by filename, then by address
    entries.sort(key=lambda x: (x["name"], x["address"]))

    # Write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {len(entries)} entries to {out_path}")


if __name__ == "__main__":
    main()

