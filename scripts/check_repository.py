#!/usr/bin/env python3
"""Reject accidentally tracked secrets, personal paths, and runtime artifacts."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SENSITIVE_NAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "token.json",
}
SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".pyc"}
TEXT_SUFFIXES = {
    "",
    ".md",
    ".py",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}
PATTERNS = {
    "private key": re.compile("-----BEGIN " + "(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile("gh" + "[pousr]_[A-Za-z0-9_]{30,}"),
    "AWS access key": re.compile("AK" + "IA[0-9A-Z]{16}"),
    "credential in URL": re.compile(r"https?://[^\s/:]+:[^\s/@]+@"),
    "personal home path": re.compile(r"(?:/home/[^/\s]+|[A-Za-z]:[\\/]Users[\\/][^\\/\s]+)"),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8")
    return [ROOT / name for name in output.rstrip("\0").split("\0") if name]


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT)
        if path.name in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            failures.append(f"sensitive file is tracked: {relative}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"unexpected binary content: {relative}")
            continue
        if relative == Path("scripts/check_repository.py"):
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{label} found in {relative}")

    if failures:
        print("Repository hygiene check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Repository hygiene check passed ({len(tracked_files())} tracked files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
