#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: $0 /path/to/mlx-stt-VERSION-macos-arm64.tar.gz" >&2
  exit 64
fi

ARCHIVE=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
if [ ! -f "$ARCHIVE" ]; then
  echo "archive does not exist: $ARCHIVE" >&2
  exit 66
fi

VERSION=$(basename "$ARCHIVE" | sed -E 's/^mlx-stt-([^-]+)-macos-arm64\.tar\.gz$/\1/')
if [ "$VERSION" = "$(basename "$ARCHIVE")" ]; then
  echo "cannot parse version from archive name: $(basename "$ARCHIVE")" >&2
  exit 65
fi

TAP_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/mlx-stt-brew-test.XXXXXX")
TAP_USER=mlx-stt-local
TAP_DIR="$(brew --repository)/Library/Taps/$TAP_USER/homebrew-tap"
INSTALLED=0
TAP_CREATED=0

cleanup() {
  if [ "$INSTALLED" -eq 1 ]; then
    brew uninstall --formula "$TAP_USER/tap/mlx-stt" >/dev/null 2>&1 || true
  fi
  if [ "$TAP_CREATED" -eq 1 ]; then
    rm -rf "$TAP_DIR"
  fi
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT INT TERM

if [ -e "$TAP_DIR" ]; then
  echo "temporary tap already exists; refusing to modify it: $TAP_DIR" >&2
  exit 70
fi

FILE_URL=$(python3 - "$ARCHIVE" <<'PY'
import sys
from pathlib import Path
print(Path(sys.argv[1]).as_uri())
PY
)

python3 "$TAP_ROOT/scripts/update_formula.py" \
  --version "$VERSION" \
  --artifact "$ARCHIVE" \
  --url "$FILE_URL" \
  --output "$WORK_DIR/mlx-stt.rb" >/dev/null

mkdir -p "$TAP_DIR/Formula"
cp "$WORK_DIR/mlx-stt.rb" "$TAP_DIR/Formula/mlx-stt.rb"
TAP_CREATED=1

brew install "$TAP_USER/tap/mlx-stt"
INSTALLED=1
brew test "$TAP_USER/tap/mlx-stt"
mlx-stt --version
printf '%s\n' "local brew install/test: ok"
