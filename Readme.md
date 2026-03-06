# SFT Practice Starter Code

This repository includes end-to-end scripts for the tutorial workflow:

1. `clean_data.py`: clean OpenOrca-style data into chat JSONL for SFT.
2. `train_sft_full_qwen05b.yaml`: LLaMA-Factory full fine-tuning config for Qwen2.5-0.5B.
3. `run_eval.sh`: run 8 required `lm_eval` tasks with required few-shot settings.
4. `summarize_eval.py`: collect lm_eval JSON outputs into a compact CSV.
5. `REPORT_TEMPLATE.md`: ready-to-fill assignment report template.

## Quickstart

```bash
python clean_data.py \
  --input data/openorca_raw.jsonl \
  --output data/openorca_cleaned.jsonl \
  --stats data/clean_stats.json

llamafactory-cli train train_sft_full_qwen05b.yaml

SFT_MODEL_DIR=outputs/qwen25_05b_openorca_full \
BATCH_SIZE=4 DEVICE=cuda:0 \
./run_eval.sh
```