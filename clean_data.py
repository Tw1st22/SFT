#!/usr/bin/env python3
"""Clean OpenOrca-style chat data for SFT.

Input supports JSON/JSONL with one sample per object.
Expected sample schema (flexible):
- messages: [{role, content}, ...]
OR
- instruction/system_prompt/question + response/output/answer

Output JSONL in chat format:
{"messages": [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]}

Also exports stats JSON.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

VALID_ROLES = {"system", "user", "assistant"}


def read_records(path: Path) -> Iterable[Dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for item in data:
            yield item
    elif isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                yield item
        else:
            yield data
    else:
        raise ValueError(f"Unsupported JSON root type: {type(data)}")


def normalize_whitespace(text: str) -> str:
    text = text.replace("\u200b", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def is_garbage(text: str, min_len: int, max_len: int) -> bool:
    t = normalize_whitespace(text)
    if len(t) < min_len or len(t) > max_len:
        return True
    alnum = sum(c.isalnum() for c in t)
    if alnum == 0:
        return True
    uniq_ratio = len(set(t)) / max(len(t), 1)
    if len(t) > 40 and uniq_ratio < 0.08:
        return True
    # repeated chunks like "abcabcabc..."
    if len(t) > 60 and re.search(r"(.{1,20})\1{4,}", t):
        return True
    return False


def canonical_messages(rec: Dict[str, Any]) -> Optional[List[Dict[str, str]]]:
    if isinstance(rec.get("messages"), list) and rec["messages"]:
        out = []
        for m in rec["messages"]:
            role = str(m.get("role", "")).strip().lower()
            if role == "human":
                role = "user"
            elif role == "bot":
                role = "assistant"
            if role not in VALID_ROLES:
                return None
            content = normalize_whitespace(str(m.get("content", "")))
            if not content:
                return None
            out.append({"role": role, "content": content})
        return out

    # fallback single-turn mapping
    prompt = rec.get("instruction") or rec.get("question") or rec.get("prompt")
    answer = rec.get("response") or rec.get("output") or rec.get("answer")
    system = rec.get("system") or rec.get("system_prompt")
    if prompt and answer:
        out = []
        if system:
            out.append({"role": "system", "content": normalize_whitespace(str(system))})
        out.append({"role": "user", "content": normalize_whitespace(str(prompt))})
        out.append({"role": "assistant", "content": normalize_whitespace(str(answer))})
        return out

    return None


def validate_turns(msgs: List[Dict[str, str]]) -> bool:
    # Must end with assistant for SFT target.
    if not msgs or msgs[-1]["role"] != "assistant":
        return False
    # No consecutive same-role turns (except optional initial system block)
    prev = None
    for i, m in enumerate(msgs):
        role = m["role"]
        if role == "system" and i == 0:
            prev = role
            continue
        if role == prev:
            return False
        prev = role
    return True


def semantic_key(msgs: List[Dict[str, str]]) -> str:
    user_parts = [m["content"].lower() for m in msgs if m["role"] == "user"]
    return "\n".join(user_parts)[:1000]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--stats", required=True)
    p.add_argument("--min-len", type=int, default=5)
    p.add_argument("--max-len", type=int, default=8192)
    args = p.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    stats_path = Path(args.stats)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stats_path.parent.mkdir(parents=True, exist_ok=True)

    counters = Counter()
    seen = set()

    with output_path.open("w", encoding="utf-8") as out:
        for rec in read_records(input_path):
            counters["total"] += 1
            msgs = canonical_messages(rec)
            if not msgs:
                counters["drop_schema"] += 1
                continue

            if not validate_turns(msgs):
                counters["drop_turns"] += 1
                continue

            if any(is_garbage(m["content"], args.min_len, args.max_len) for m in msgs):
                counters["drop_quality"] += 1
                continue

            key = semantic_key(msgs)
            if key in seen:
                counters["drop_dup_semantic"] += 1
                continue
            seen.add(key)

            out.write(json.dumps({"messages": msgs}, ensure_ascii=False) + "\n")
            counters["kept"] += 1

    counters["keep_ratio"] = round(counters["kept"] / max(counters["total"], 1), 4)
    stats_path.write_text(json.dumps(counters, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(counters, ensure_ascii=False))


if __name__ == "__main__":
    main()