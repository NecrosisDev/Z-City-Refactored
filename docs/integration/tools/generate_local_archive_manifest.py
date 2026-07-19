#!/usr/bin/env python3
"""Generate the canonical local-archive file manifest used by the Z-City recovery audit.

The script is intentionally standalone and uses only Python's standard library.
It never extracts or modifies runtime source files; it streams each ZIP member,
normalizes the deployment wrapper, computes content identities, and writes CSV.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import zipfile
from pathlib import Path, PurePosixPath

EXPECTED_ARCHIVE_SHA256 = "0286d0f25f9744cc6387e8676e9429ef11a8991bbad6bda45961f4358b534652"
EXPECTED_MANIFEST_SHA256 = "28f6eca648b80d6eca1419ce3e30fc60d2971ab743457d23aeee9d5a261cd4b0"
EXPECTED_FILE_COUNT = 1040
WRAPPER = "TMod/"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_path(member_name: str) -> str:
    path = PurePosixPath(member_name).as_posix()
    if path.startswith(WRAPPER):
        path = path[len(WRAPPER) :]
    return path.lstrip("/")


def candidate_path(path: str) -> str:
    prefix = "gamemodes/trauma/"
    if path.startswith(prefix):
        return "gamemodes/zcity/" + path[len(prefix) :]
    return path


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def write_manifest(zip_path: Path, output_path: Path) -> int:
    archive_hash = sha256_file(zip_path)
    if archive_hash != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(
            f"Archive SHA-256 mismatch: expected {EXPECTED_ARCHIVE_SHA256}, got {archive_hash}"
        )

    rows: list[tuple[str, str, int, str, str]] = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            path = normalize_path(info.filename)
            if not path:
                continue
            data = archive.read(info)
            rows.append(
                (
                    path,
                    candidate_path(path),
                    len(data),
                    hashlib.sha256(data).hexdigest(),
                    git_blob_sha1(data),
                )
            )

    rows.sort(key=lambda row: row[0])
    if len(rows) != EXPECTED_FILE_COUNT:
        raise ValueError(f"File-count mismatch: expected {EXPECTED_FILE_COUNT}, got {len(rows)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["path", "baseline_candidate_path", "size_bytes", "sha256", "git_blob_sha1"]
        )
        writer.writerows(rows)

    manifest_hash = sha256_file(output_path)
    if manifest_hash != EXPECTED_MANIFEST_SHA256:
        raise ValueError(
            f"Manifest SHA-256 mismatch: expected {EXPECTED_MANIFEST_SHA256}, got {manifest_hash}"
        )
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Path to the pinned Trauma.zip archive")
    parser.add_argument("output", type=Path, help="Destination CSV path")
    args = parser.parse_args()

    try:
        count = write_manifest(args.archive, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {count} rows to {args.output}")
    print(f"manifest_sha256={EXPECTED_MANIFEST_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
