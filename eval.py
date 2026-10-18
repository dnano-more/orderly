#!/usr/bin/env python3
"""Measure order accuracy. Cases live in eval/cases.jsonl, one per line:
{"text": "do kilo cheeni, 1 litre tel", "items": [["sugar", 2], ["cooking oil", 1]]}
Items are the catalogue names you expect and the quantity.

Usage: python eval.py --model gemma3:4b      (or --offline for the rule-based parser)
"""
import argparse
import json
from pathlib import Path

import orderly as O


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemma3:4b")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cases", default="eval/cases.jsonl")
    a = ap.parse_args()
    cases = [json.loads(l) for l in Path(a.cases).read_text(encoding="utf-8").splitlines() if l.strip()]
    tp = fp = fn = exact = 0
    for c in cases:
        r = O.handle_order(c["text"], a.model, a.offline)
        got = {(l["item"], float(l["qty"])) for l in r["invoice"]["lines"] if l["amount"] is not None}
        want = {(n, float(q)) for n, q in c["items"]}
        tp += len(got & want)
        fp += len(got - want)
        fn += len(want - got)
        exact += got == want
        if got != want:
            print(f"MISS [{r['method']}] {c['text']!r}\n   want {sorted(want)}\n   got  {sorted(got)}")
    p = tp / (tp + fp) if tp + fp else 0
    rc = tp / (tp + fn) if tp + fn else 0
    print(f"\n{len(cases)} messages | whole order exact: {exact}/{len(cases)} "
          f"| item precision {p:.0%} | item recall {rc:.0%}")


if __name__ == "__main__":
    main()
