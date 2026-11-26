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


def update_formula_text(text, *, version, sha256, url, owner):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version):
        raise ValueError("version must look like a semantic version: " + version)
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ValueError("sha256 must be 64 lowercase hexadecimal characters")
    if not re.match(r"(https|file)://", url):
        raise ValueError("url must start with https:// or file://")

    updated = text
    updated = replace_once(updated, r'^  homepage ".*"$', '  homepage "https://github.com/{}/mlx-stt"'.format(owner), "homepage")
    updated = replace_once(updated, r'^  version ".*"$', '  version "{}"'.format(version), "version")
    updated = replace_once(updated, r'^  url ".*"$', '  url "{}"'.format(url), "url")
    updated = replace_once(updated, r'^  sha256 ".*"$', '  sha256 "{}"'.format(sha256), "sha256")
    return updated


def release_url(owner, version):
    artifact = "mlx-stt-{}-macos-arm64.tar.gz".format(version)
    return "https://github.com/{}/mlx-stt/releases/download/v{}/{}".format(owner, version, artifact)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Update or render Formula/mlx-stt.rb")
    parser.add_argument("--version", required=True)
    parser.add_argument("--sha256", help="artifact sha256; omit when --artifact is supplied")
    parser.add_argument("--artifact", type=Path, help="local artifact used to compute sha256")
    parser.add_argument("--url", help="artifact URL; defaults to the GitHub release URL")
    parser.add_argument("--owner", default="wizicer", help="GitHub owner used in homepage and default release URL")
    parser.add_argument("--formula", type=Path, default=DEFAULT_FORMULA, help="input formula path")
    parser.add_argument("--output", type=Path, help="write rendered formula here instead of updating in place")
    args = parser.parse_args(argv)

    if args.sha256 and args.artifact:
        parser.error("pass either --sha256 or --artifact, not both")
    digest = args.sha256 or (sha256_file(args.artifact.expanduser().resolve()) if args.artifact else None)
    if digest is None:
        parser.error("pass --sha256 or --artifact")
    url = args.url or release_url(args.owner, args.version)

    formula = args.formula.expanduser().resolve()
    try:
        rendered = update_formula_text(
            formula.read_text(encoding="utf-8"),
            version=args.version,
            sha256=digest.lower(),
            url=url,
            owner=args.owner,
        )
    except (OSError, ValueError) as exc:
        print("update_formula: error: {}".format(exc), file=sys.stderr)
        return 2

    destination = args.output.expanduser().resolve() if args.output else formula
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    print("wrote {}".format(destination))
    print("url: {}".format(url))
    print("sha256: {}".format(digest.lower()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
