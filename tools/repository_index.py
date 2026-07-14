#!/usr/bin/env python3
"""Generate deterministic repository manifests for offline symbol and registration lookup."""

from __future__ import annotations

import hashlib
import json
import keyword
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "generated" / "repository"
SYMBOL_DIR = OUT / "symbols"

SOURCE_ROOTS = ("lua", "gamemodes", "entities", "weapons", "effects")
TEXT_EXTENSIONS = {
    ".lua", ".txt", ".md", ".json", ".vmt", ".vmf", ".cfg", ".ini",
    ".xml", ".properties", ".csv", ".yml", ".yaml",
}
LUA_KEYWORDS = {
    "and", "break", "continue", "do", "else", "elseif", "end", "false",
    "for", "function", "goto", "if", "in", "local", "nil", "not", "or",
    "repeat", "return", "then", "true", "until", "while",
}

IDENTIFIER_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"([A-Za-z_][A-Za-z0-9_]*(?:(?:[.:])[A-Za-z_][A-Za-z0-9_]*)*)"
)
FUNCTION_PATTERNS = (
    re.compile(r"^\s*local\s+function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
    re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_:.]*)\s*\("),
    re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_:.]*)\s*=\s*function\s*\("),
)
REGISTRATION_PATTERNS = {
    "hook_add": re.compile(r"\bhook\.Add\s*\(\s*([\"'])(.*?)\1"),
    "hook_remove": re.compile(r"\bhook\.Remove\s*\(\s*([\"'])(.*?)\1"),
    "hook_run": re.compile(r"\bhook\.(?:Run|Call)\s*\(\s*([\"'])(.*?)\1"),
    "timer_create": re.compile(r"\btimer\.Create\s*\(\s*([\"'])(.*?)\1"),
    "timer_remove": re.compile(r"\btimer\.Remove\s*\(\s*([\"'])(.*?)\1"),
    "timer_adjust": re.compile(r"\btimer\.Adjust\s*\(\s*([\"'])(.*?)\1"),
    "timer_simple": re.compile(r"\btimer\.Simple\s*\("),
    "net_declare": re.compile(r"\butil\.AddNetworkString\s*\(\s*([\"'])(.*?)\1"),
    "net_receive": re.compile(r"\bnet\.Receive\s*\(\s*([\"'])(.*?)\1"),
    "net_start": re.compile(r"\bnet\.Start\s*\(\s*([\"'])(.*?)\1"),
    "concommand_add": re.compile(r"\bconcommand\.Add\s*\(\s*([\"'])(.*?)\1"),
    "create_convar": re.compile(r"\bCreateConVar\s*\(\s*([\"'])(.*?)\1"),
    "create_client_convar": re.compile(r"\bCreateClientConVar\s*\(\s*([\"'])(.*?)\1"),
    "include": re.compile(r"\binclude\s*\(\s*([\"'])(.*?)\1"),
    "addcsluafile": re.compile(r"\bAddCSLuaFile\s*\(\s*([\"'])(.*?)\1"),
    "workshop": re.compile(r"\bresource\.AddWorkshop\s*\(\s*([\"'])(.*?)\1"),
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def should_skip(path: Path) -> bool:
    rel = relative(path)
    if rel.startswith("docs/generated/"):
        return True
    return any(part in {".git", "__pycache__"} for part in path.parts)


def iter_files() -> Iterable[Path]:
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and not should_skip(path):
            yield path


def is_probably_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def read_text(path: Path) -> str | None:
    if not is_probably_text(path):
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
    except OSError:
        return None


def source_file(path: Path) -> bool:
    rel = relative(path)
    return any(rel == root or rel.startswith(f"{root}/") for root in SOURCE_ROOTS)


def shard_for(symbol: str) -> str:
    first = symbol[0].lower()
    if first.isalpha():
        return first
    if first.isdigit():
        return "0-9"
    return "_"


def normalize_line(line: str) -> str:
    return " ".join(line.strip().split())[:300]


def extract_literal(match: re.Match[str]) -> str:
    if match.lastindex and match.lastindex >= 2:
        return match.group(2)
    return "<dynamic>"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SYMBOL_DIR.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    registrations: dict[str, list[dict[str, object]]] = defaultdict(list)
    definitions: list[dict[str, object]] = []
    symbol_rows: dict[str, list[str]] = defaultdict(list)
    symbol_counts: Counter[str] = Counter()
    file_count = 0
    lua_count = 0
    total_bytes = 0

    for path in iter_files():
        rel = relative(path)
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        text = read_text(path)
        line_count = text.count("\n") + 1 if text is not None and text else 0
        manifest.append({
            "path": rel,
            "size_bytes": len(data),
            "sha256": digest,
            "extension": path.suffix.lower(),
            "line_count": line_count,
            "is_source": source_file(path),
            "is_text": text is not None,
        })
        file_count += 1
        total_bytes += len(data)

        if path.suffix.lower() != ".lua" or text is None:
            continue

        lua_count += 1
        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            excerpt = normalize_line(raw_line)
            if not excerpt:
                continue

            for pattern in FUNCTION_PATTERNS:
                match = pattern.search(raw_line)
                if match:
                    definitions.append({
                        "symbol": match.group(1),
                        "path": rel,
                        "line": line_number,
                        "excerpt": excerpt,
                    })
                    break

            for category, pattern in REGISTRATION_PATTERNS.items():
                for match in pattern.finditer(raw_line):
                    registrations[category].append({
                        "name": extract_literal(match),
                        "path": rel,
                        "line": line_number,
                        "excerpt": excerpt,
                    })

            seen_on_line: set[str] = set()
            for symbol in IDENTIFIER_RE.findall(raw_line):
                if symbol in LUA_KEYWORDS or keyword.iskeyword(symbol):
                    continue
                if len(symbol) < 3 or symbol in seen_on_line:
                    continue
                seen_on_line.add(symbol)
                symbol_counts[symbol] += 1
                shard = shard_for(symbol)
                safe_excerpt = excerpt.replace("\t", " ")
                symbol_rows[shard].append(
                    f"{symbol}\t{rel}\t{line_number}\t{safe_excerpt}"
                )

    manifest.sort(key=lambda item: str(item["path"]))
    definitions.sort(key=lambda item: (str(item["symbol"]).lower(), str(item["path"]), int(item["line"])))
    for rows in symbol_rows.values():
        rows.sort(key=lambda row: (row.split("\t", 1)[0].lower(), row))

    (OUT / "file-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT / "lua-registrations.json").write_text(
        json.dumps(
            {key: sorted(value, key=lambda item: (str(item["name"]), str(item["path"]), int(item["line"])))
             for key, value in sorted(registrations.items())},
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    (OUT / "lua-definitions.json").write_text(
        json.dumps(definitions, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    for old in SYMBOL_DIR.glob("*.tsv"):
        old.unlink()
    for shard, rows in sorted(symbol_rows.items()):
        (SYMBOL_DIR / f"{shard}.tsv").write_text(
            "symbol\tpath\tline\texcerpt\n" + "\n".join(rows) + "\n",
            encoding="utf-8",
        )

    catalog = {
        "format_version": 1,
        "file_count": file_count,
        "lua_file_count": lua_count,
        "total_bytes": total_bytes,
        "symbols": len(symbol_counts),
        "symbol_occurrences": sum(symbol_counts.values()),
        "registration_counts": {key: len(value) for key, value in sorted(registrations.items())},
        "shards": {
            shard: {
                "path": f"docs/generated/repository/symbols/{shard}.tsv",
                "occurrences": len(rows),
            }
            for shard, rows in sorted(symbol_rows.items())
        },
    }
    (OUT / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    summary_lines = [
        "# Generated Repository Index",
        "",
        "This directory is generated by `tools/repository_index.py`.",
        "Do not edit generated files manually.",
        "",
        "## Snapshot",
        "",
        f"- Files: **{file_count:,}**",
        f"- Lua files: **{lua_count:,}**",
        f"- Total bytes: **{total_bytes:,}**",
        f"- Distinct indexed symbols: **{len(symbol_counts):,}**",
        f"- Symbol occurrences: **{sum(symbol_counts.values()):,}**",
        "",
        "## Files",
        "",
        "- `file-manifest.json`: every repository file with size, hash, type, and line count.",
        "- `lua-definitions.json`: lexical Lua function definitions.",
        "- `lua-registrations.json`: hooks, timers, networking, commands, ConVars, includes, and Workshop registrations.",
        "- `symbols/*.tsv`: exhaustive lexical Lua symbol occurrences, sharded by first character.",
        "- `catalog.json`: counts and shard metadata.",
        "",
        "## Lookup",
        "",
        "Choose the shard matching the first character of the symbol. For example,",
        "`RagdollFunc` is stored in `symbols/r.tsv`.",
        "",
        "The index is lexical. Dynamic names, generated code, comments, strings, and aliases",
        "still require semantic review before conclusions are treated as verified.",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(summary_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
