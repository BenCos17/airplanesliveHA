#!/usr/bin/env python3
"""Bump add-on version and prepend a changelog entry.

This script updates version references in:
- AirplanesLiveHA/config.yaml
- AirplanesLiveHA/run.py
- AirplanesLiveHA/Dockerfile
- AirplanesLiveHA/DOCS.md
- AirplanesLiveHA/TROUBLESHOOTING.md
- AirplanesLiveHA/CHANGELOG.md
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Callable

ROOT = pathlib.Path(__file__).resolve().parents[2]
ADDON_DIR = ROOT / "AirplanesLiveHA"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bump version and changelog")
    parser.add_argument(
        "--bump",
        choices=["patch", "minor", "major"],
        required=True,
        help="SemVer segment to increment",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional release notes, one bullet per line",
    )
    return parser.parse_args()


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: pathlib.Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def replace_exactly_once(
    text: str,
    pattern: str,
    repl_builder: Callable[[re.Match[str]], str],
    label: str,
) -> str:
    regex = re.compile(pattern, re.MULTILINE)
    matches = list(regex.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one match for {label}, found {len(matches)}")
    return regex.sub(lambda m: repl_builder(m), text, count=1)


def parse_version(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise RuntimeError(f"Invalid version format: {version}")
    major_s, minor_s, patch_s = match.groups()
    return int(major_s), int(minor_s), int(patch_s)


def bump_version(version: str, bump: str) -> str:
    major, minor, patch = parse_version(version)
    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "patch":
        patch += 1
    else:
        raise RuntimeError(f"Unsupported bump type: {bump}")
    return f"{major}.{minor}.{patch}"


def get_current_version() -> str:
    config_path = ADDON_DIR / "config.yaml"
    config_text = read_text(config_path)
    match = re.search(r'^version:\s*"(\d+\.\d+\.\d+)"\s*$', config_text, re.MULTILINE)
    if not match:
        raise RuntimeError("Unable to find version in AirplanesLiveHA/config.yaml")
    return match.group(1)


def update_versions(old_version: str, new_version: str) -> None:
    updates = [
        (
            ADDON_DIR / "config.yaml",
            r'^(version:\s*")(\d+\.\d+\.\d+)("\s*)$',
            lambda m: f"{m.group(1)}{new_version}{m.group(3)}",
            "config.yaml version",
        ),
        (
            ADDON_DIR / "run.py",
            r'^(DEFAULT_ADDON_VERSION\s*=\s*")(\d+\.\d+\.\d+)("\s*)$',
            lambda m: f"{m.group(1)}{new_version}{m.group(3)}",
            "run.py DEFAULT_ADDON_VERSION",
        ),
        (
            ADDON_DIR / "Dockerfile",
            r'^(ARG\s+ADDON_VERSION=)(\d+\.\d+\.\d+)(\s*)$',
            lambda m: f"{m.group(1)}{new_version}{m.group(3)}",
            "Dockerfile ARG ADDON_VERSION",
        ),
        (
            ADDON_DIR / "DOCS.md",
            r'^(\-\s*\*\*Version\*\*:\s*)(\d+\.\d+\.\d+)(\s*)$',
            lambda m: f"{m.group(1)}{new_version}{m.group(3)}",
            "DOCS.md Version",
        ),
        (
            ADDON_DIR / "TROUBLESHOOTING.md",
            r'^(\[INFO\]\s+Starting\s+Airplanes\s+Live\s+Home\s+Assistant\s+Add-on\s+v)(\d+\.\d+\.\d+)(\s*)$',
            lambda m: f"{m.group(1)}{new_version}{m.group(3)}",
            "TROUBLESHOOTING.md startup log version",
        ),
    ]

    for path, pattern, builder, label in updates:
        text = read_text(path)
        # Guard against unexpected stale replacement context.
        if old_version not in text:
            raise RuntimeError(f"Expected old version {old_version} not found in {path}")
        updated = replace_exactly_once(text, pattern, builder, label)
        write_text(path, updated)


def normalize_notes(notes: str) -> list[str]:
    lines = [line.strip() for line in notes.splitlines() if line.strip()]
    normalized: list[str] = []
    for line in lines:
        if line.startswith("- "):
            normalized.append(line)
        else:
            normalized.append(f"- {line}")
    return normalized


def update_changelog(new_version: str, notes: str) -> None:
    changelog_path = ADDON_DIR / "CHANGELOG.md"
    changelog = read_text(changelog_path)

    if re.search(rf"^##\s+{re.escape(new_version)}\s*$", changelog, re.MULTILINE):
        raise RuntimeError(f"CHANGELOG already contains version {new_version}")

    note_lines = normalize_notes(notes)
    if not note_lines:
        note_lines = [
            "- Automated release version bump",
        ]

    entry = "\n".join([f"## {new_version}", *note_lines, ""]) + "\n"
    updated = entry + changelog.lstrip("\n")
    write_text(changelog_path, updated)


def main() -> int:
    args = parse_args()
    old_version = get_current_version()
    new_version = bump_version(old_version, args.bump)

    update_versions(old_version, new_version)
    update_changelog(new_version, args.notes)

    print(f"Bumped version: {old_version} -> {new_version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
