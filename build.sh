#!/usr/bin/env bash
# Pack the app into build/<app>.tgz, skipping everything matched by .gitignore.
# If on Windows, run from Git Bash
set -euo pipefail

cd "$(dirname "$0")"
APP_NAME="$(basename "$PWD")"
OUT="build/${APP_NAME}.tgz"

STAGE="build/stage"

# Stage the files under build/stage/<app>/ and tar that folder, so the archive
# has real directory entries (SOAR's installer needs the top-level app dir).
rm -rf "$STAGE"
mkdir -p "$STAGE/$APP_NAME"
git ls-files -z --cached --others --exclude-standard \
  | tar --null -cf - -T - \
  | tar -xf - -C "$STAGE/$APP_NAME"
tar -czf "$OUT" --owner=0 --group=0 --numeric-owner -C "$STAGE" "$APP_NAME"
rm -rf "$STAGE"

echo "Built $OUT"
