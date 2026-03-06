#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   SFT_MODEL_DIR=outputs/qwen25_05b_openorca_full BATCH_SIZE=4 DEVICE=cuda:0 ./run_eval.sh

: "${SFT_MODEL_DIR:?Please set SFT_MODEL_DIR}"
OUT_DIR="${OUT_DIR:-lm_eval_results/$(date +%Y%m%d_%H%M%S)}"
BATCH_SIZE="${BATCH_SIZE:-4}"
DEVICE="${DEVICE:-cuda:0}"

mkdir -p "$OUT_DIR"
MODEL_ARGS="pretrained=${SFT_MODEL_DIR},trust_remote_code=True,dtype=float16"

run_task() {
  local task="$1"
  local fewshot="$2"
  local out_json="$OUT_DIR/${task}_fs${fewshot}.json"

  echo "==> Running ${task} (fewshot=${fewshot})"
  python -m lm_eval \
    --model hf \
    --model_args "$MODEL_ARGS" \
    --tasks "$task" \
    --num_fewshot "$fewshot" \
    --device "$DEVICE" \
    --batch_size "$BATCH_SIZE" \
    --apply_chat_template \
    --output_path "$out_json"
}

run_task mmlu 5
run_task arc_easy 0
run_task arc_challenge 25
run_task hellaswag 10
run_task winogrande 5
run_task truthfulqa_mc2 0
run_task piqa 0
run_task boolq 0

echo "Saved raw lm_eval outputs to: $OUT_DIR"
python summarize_eval.py --input_dir "$OUT_DIR" --output "$OUT_DIR/summary.csv"