#!/usr/bin/env python3
"""Update or render the mlx-stt Homebrew formula.

The same script is used for release updates and for local file:// testing.
It intentionally has no third-party dependencies and remains compatible with
the Python 3 version shipped by macOS.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FORMULA = ROOT / "Formula" / "mlx-stt.rb"


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def replace_once(text, pattern, replacement, label):
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError("Formula does not contain exactly one " + label)
    return updated


def update_formula_text(
    text,
    *,
    version,
    sha256_macos15,
    url_macos15,
    sha256_macos26,
    url_macos26,
    owner,
):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version):
        raise ValueError("version must look like a semantic version: " + version)
    for label, digest in (("macOS 15", sha256_macos15), ("macOS 26", sha256_macos26)):
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(label + " sha256 must be 64 lowercase hexadecimal characters")
    for label, url in (("macOS 15", url_macos15), ("macOS 26", url_macos26)):
        if not re.match(r"(https|file)://", url):
            raise ValueError(label + " url must start with https:// or file://")

    updated = text
    updated = replace_once(updated, r'^  homepage ".*"$', '  homepage "https://github.com/{}/mlx-stt"'.format(owner), "homepage")
    updated = replace_once(updated, r'^  version ".*"$', '  version "{}"'.format(version), "version")
    updated = replace_once(
        updated,
        r'(on_tahoe :or_newer do\n    url )"[^"]+"\n    sha256 "[^"]+"',
        r'\g<1>"{}"\n    sha256 "{}"'.format(url_macos26, sha256_macos26),
        "macOS 26 url/sha256",
    )
    updated = replace_once(
        updated,
        r'(on_sequoia do\n    url )"[^"]+"\n    sha256 "[^"]+"',
        r'\g<1>"{}"\n    sha256 "{}"'.format(url_macos15, sha256_macos15),
        "macOS 15 url/sha256",
    )
    return updated


def release_url(owner, version, macos_target):
    artifact = "mlx-stt-{}-macos{}-arm64.tar.gz".format(version, macos_target)
    return "https://github.com/{}/mlx-stt/releases/download/v{}/{}".format(owner, version, artifact)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Update or render Formula/mlx-stt.rb")
    parser.add_argument("--version", required=True)
    parser.add_argument("--sha256", help="artifact sha256 used for both macOS targets unless overridden")
    parser.add_argument("--sha256-macos15", help="macOS 15 artifact sha256")
    parser.add_argument("--sha256-macos26", help="macOS 26 artifact sha256")
    parser.add_argument("--artifact", type=Path, help="local artifact used to compute a sha256 for both targets")
    parser.add_argument("--url", help="artifact URL used for both macOS targets unless overridden")
    parser.add_argument("--url-macos15", help="macOS 15 artifact URL")
    parser.add_argument("--url-macos26", help="macOS 26 artifact URL")
    parser.add_argument("--owner", default="wizicer", help="GitHub owner used in homepage and default release URL")
    parser.add_argument("--formula", type=Path, default=DEFAULT_FORMULA, help="input formula path")
    parser.add_argument("--output", type=Path, help="write rendered formula here instead of updating in place")
    args = parser.parse_args(argv)

    if args.sha256 and args.artifact:
        parser.error("pass either --sha256 or --artifact, not both")
    artifact_digest = sha256_file(args.artifact.expanduser().resolve()) if args.artifact else None
    base_digest = args.sha256 or artifact_digest
    digest_macos15 = args.sha256_macos15 or base_digest
    digest_macos26 = args.sha256_macos26 or base_digest
    if digest_macos15 is None or digest_macos26 is None:
        parser.error("pass --artifact/--sha256 or both --sha256-macos15 and --sha256-macos26")

    url_macos15 = args.url_macos15 or args.url or release_url(args.owner, args.version, "15")
    url_macos26 = args.url_macos26 or args.url or release_url(args.owner, args.version, "26")

    formula = args.formula.expanduser().resolve()
    try:
        rendered = update_formula_text(
            formula.read_text(encoding="utf-8"),
            version=args.version,
            sha256_macos15=digest_macos15.lower(),
            url_macos15=url_macos15,
            sha256_macos26=digest_macos26.lower(),
            url_macos26=url_macos26,
            owner=args.owner,
        )
    except (OSError, ValueError) as exc:
        print("update_formula: error: {}".format(exc), file=sys.stderr)
        return 2

    destination = args.output.expanduser().resolve() if args.output else formula
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    print("wrote {}".format(destination))
    print("macOS 15 url: {}".format(url_macos15))
    print("macOS 15 sha256: {}".format(digest_macos15.lower()))
    print("macOS 26 url: {}".format(url_macos26))
    print("macOS 26 sha256: {}".format(digest_macos26.lower()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
