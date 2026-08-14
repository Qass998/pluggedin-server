#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/taoufik123-collab/claude-watch.git"
PINNED_COMMIT="7711231e4c47e5d4e06bcf5326c4abf5b70ab4a9"
TARGET=".vendor/claude-watch"

command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg is required" >&2; exit 1; }
command -v yt-dlp >/dev/null || { echo "yt-dlp is required" >&2; exit 1; }

mkdir -p .vendor

if [ ! -d "$TARGET/.git" ]; then
  git clone "$REPO_URL" "$TARGET"
fi

git -C "$TARGET" fetch origin "$PINNED_COMMIT" --depth 1
git -C "$TARGET" checkout --detach "$PINNED_COMMIT"

echo "claude-watch installed at $TARGET"
echo "Pinned commit: $PINNED_COMMIT"
echo "Optional Whisper fallback: set GROQ_API_KEY or OPENAI_API_KEY."
