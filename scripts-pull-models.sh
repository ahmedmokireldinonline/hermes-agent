#!/usr/bin/env bash
set -euo pipefail

# Pull only models selected for the requested profile.
# Usage: PROFILE=lite ./scripts-pull-models.sh
PROFILE="${PROFILE:-lite}"
OLLAMA_BIN="${OLLAMA_BIN:-ollama}"

case "$PROFILE" in
  lite)
    MODELS=(qwen3:4b qwen3:8b qwen2.5-coder:7b granite3.3:8b bge-m3)
    ;;
  balanced)
    MODELS=(qwen3:4b qwen3:14b deepseek-r1:14b qwen2.5-coder:14b mistral-small3.1:24b bge-m3)
    ;;
  quality)
    MODELS=(qwen3:8b qwen3:32b deepseek-r1:32b qwen2.5-coder:32b mistral-small3.1:24b bge-m3)
    ;;
  *) echo "Unknown PROFILE: $PROFILE (use lite, balanced, or quality)" >&2; exit 2 ;;
esac

for model in "${MODELS[@]}"; do
  echo "Pulling $model"
  "$OLLAMA_BIN" pull "$model"
done

echo "Done. Review model licenses in config/models.open.yaml before redistribution."
