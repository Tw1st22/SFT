# AIMS5740 Homework 1 — SFT Practice Report

> Suggested length: 2–4 pages.

## 1. Experiment Setup
- Student ID / Name:
- Base model: `Qwen/Qwen2.5-0.5B`
- Dataset: `Open-Orca/OpenOrca`
- Deterministic subset revision: `e9c87b4`
- Subset size loaded: `1,000,000`
- Cleaned target size used (200k–350k):
- Framework: `LLaMA-Factory`
- Finetuning type: `full`
- Hardware / GPU:
- Seed:

## 2. Data Cleaning Strategy
### 2.1 Rules
- Formatting cleanup:
- Quality filtering:
- Consistency / dedup:

### 2.2 Data statistics
Paste key numbers from `artifacts/clean_stats.json`:
- total:
- kept:
- drop_schema:
- drop_turns:
- drop_quality:
- drop_dup:

## 3. SFT Training
### 3.1 Hyperparameters
- learning_rate:
- batch_size (per device):
- gradient_accumulation_steps:
- effective batch size:
- epochs:
- warmup ratio/steps:
- weight_decay:
- max_seq_len:
- optimizer:

### 3.2 Training behavior
- Loss curve trend:
- Perplexity trend (if available):
- Notes about convergence / instability:

## 4. Evaluation (base vs SFT)
All tasks with `apply_chat_template=True`.

| Task | Few-shot | Base score | SFT score | Δ (SFT-Base) |
|---|---:|---:|---:|---:|
| mmlu | 5 |  |  |  |
| arc_easy | 0 |  |  |  |
| arc_challenge | 25 |  |  |  |
| hellaswag | 10 |  |  |  |
| winogrande | 5 |  |  |  |
| truthfulqa_mc2 | 0 |  |  |  |
| piqa | 0 |  |  |  |
| boolq | 0 |  |  |  |

> You can directly attach/export `artifacts/base_vs_sft.csv`.

## 5. Manual Behavior Check (qualitative)
Provide a few prompts and compare base vs SFT responses.
- Prompt 1:
- Base output:
- SFT output:
- Brief judgment:

## 6. Conclusion & Analysis
- What improved:
- What did not improve:
- Main bottlenecks:
- Next-step tuning ideas:

## 7. Submission checklist
- [ ] Complete training script (.ipynb or .py)
- [ ] Key training logs (hyperparameters + loss/perplexity evidence)
- [ ] Evaluation scores for base and SFT (8 tasks)
- [ ] Brief report (2–4 pages)
- [ ] Zip name: `StudentID_Name_AIMS5740_Homework1.zip`
- [ ] Zip size < 10MB (exclude checkpoints/datasets)