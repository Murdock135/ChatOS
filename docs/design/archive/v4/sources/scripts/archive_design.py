"""Archive public design sources and verify immutable version manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def public_sources(repository: Path, version: str) -> list[Path]:
    """Select only repository-owned frontend, design documentation, and evidence."""
    files = list((repository / "frontend/src").rglob("*"))
    files += [
        repository / name
        for name in [
            "frontend/public/app.js",
            "frontend/public/theme.js",
            "frontend/public/geist-OFL.txt",
            "src/chatos/web.py",
            "tests/test_web.py",
            "scripts/archive_design.py",
            "tests/test_design_archive.py",
            "AGENTS.md",
            "frontend/public/smriti-icon.svg",
            "frontend/public/smriti-brand.svg",
            "frontend/public/smriti-brand.png",
            "frontend/astro.config.mjs",
            "docs/design/STYLEGUIDE.md",
            "docs/design/CHANGELOG.md",
            "docs/design/REFERENCES.md",
            "docs/design/sources/modern-dark-v2.txt",
            "docs/design/README.md",
            "docs/adr/0011-interface-design-system.md",
            "docs/adr/0012-modern-dark-style.md",
            "docs/adr/0013-conversation-first-workspace.md",
            "docs/adr/0014-unified-conversation-explorer.md",
        ]
    ]
    files += list((repository / "docs/design/evidence" / version).glob("*"))
    selected = []
    for file in files:
        if file.is_symlink():
            raise ValueError("Design archive inputs cannot be symlinks")
        if not file.is_file():
            continue
        relative = file.relative_to(repository)
        if any(part.startswith(".") for part in relative.parts):
            continue
        is_evidence = repository / "docs/design/evidence" / version in file.parents
        is_font = repository / "frontend/src/assets/fonts" in file.parents
        is_design_source = relative == Path("docs/design/sources/modern-dark-v2.txt")
        is_font_license = relative == Path("frontend/public/geist-OFL.txt")
        allowed_special = (
            (is_evidence and file.suffix.lower() == ".json")
            or (is_font and file.suffix.lower() in {".woff2", ".txt"})
            or is_design_source
            or is_font_license
        )
        if not allowed_special and file.suffix.lower() not in {
            ".astro",
            ".css",
            ".ts",
            ".js",
            ".py",
            ".md",
            ".svg",
            ".png",
        }:
            continue
        if repository.resolve() not in file.resolve().parents:
            raise ValueError("Design input escapes the repository")
        selected.append(file)
    return sorted(set(selected))


def git_provenance(repository: Path) -> dict:
    def command(arguments: list[str]) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"

    return {
        "head": command(["rev-parse", "HEAD"]),
        "public_working_tree": command(
            [
                "status",
                "--short",
                "--",
                "frontend",
                "docs/design",
                "docs/adr/0011-interface-design-system.md",
                "scripts/archive_design.py",
            ]
        ),
        "interpretation": "Sources are copied from the current working tree, including uncommitted changes. HEAD is a base reference, not a claim that these sources are committed.",
    }


def create_archive(
    repository: Path, version: str, source_ref: str, summary: str
) -> Path:
    """Capture a new version, refusing to replace an existing archive."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,63}", version) or ".." in version:
        raise ValueError("Choose a simple version such as v1 or v1.1")
    if not source_ref.strip() or not summary.strip():
        raise ValueError("Source reference and summary are required")
    guide = repository / "docs/design/STYLEGUIDE.md"
    evidence = repository / "docs/design/evidence" / version / "README.md"
    if not guide.is_file() or not evidence.is_file():
        raise ValueError(
            "The active guide and version evidence README must exist before archival"
        )
    target = repository / "docs/design/archive" / version
    inputs = public_sources(repository, version)
    target.mkdir(parents=True, exist_ok=False)
    entries = []
    for file in inputs:
        relative = file.relative_to(repository)
        output = target / "sources" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, output)
        entries.append(
            {
                "path": str(output.relative_to(target)),
                "source": str(relative),
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "bytes": output.stat().st_size,
            }
        )
    manifest = {
        "schema_version": 1,
        "version": version,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source_ref": source_ref,
        "summary": summary,
        "authority": "User-requested redesign; specific design choices delegated to the assistant. User visual acceptance is not inferred.",
        "git": git_provenance(repository),
        "files": entries,
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return target


def verify_archive(archive: Path) -> dict:
    """Validate every archived file against its recorded hash and reject extras."""
    manifest = json.loads((archive / "manifest.json").read_text())
    expected = {"manifest.json"}
    for entry in manifest["files"]:
        relative = Path(entry["path"])
        file = archive / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or file.is_symlink()
            or archive.resolve() not in file.resolve().parents
        ):
            raise ValueError("Unsafe archive file path")
        if (
            not file.is_file()
            or hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]
        ):
            raise ValueError("Archive integrity mismatch: " + str(relative))
        expected.add(str(relative))
    actual = {
        str(file.relative_to(archive)) for file in archive.rglob("*") if file.is_file()
    }
    if actual != expected:
        raise ValueError("Archive contains files absent from its manifest")
    return {
        "version": manifest.get("version", "observed-baseline"),
        "verified_files": len(manifest["files"]),
        "ok": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version")
    parser.add_argument("--source-ref")
    parser.add_argument("--summary")
    parser.add_argument("--check", metavar="VERSION")
    arguments = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    if arguments.check:
        if (
            not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,63}", arguments.check)
            or ".." in arguments.check
        ):
            parser.error("Invalid archive version")
        target = repository / "docs/design/archive" / arguments.check
    elif arguments.version and arguments.source_ref and arguments.summary:
        target = create_archive(
            repository, arguments.version, arguments.source_ref, arguments.summary
        )
    else:
        parser.error(
            "Provide --version, --source-ref and --summary, or --check VERSION"
        )
    print(json.dumps(verify_archive(target)))


if __name__ == "__main__":
    main()
