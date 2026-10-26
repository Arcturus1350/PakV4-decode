#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepare Luoyang battle skill scripts for batch decompile, sorted by boss 1-5."""

import re
import shutil
from pathlib import Path

# repo root: .../PakV4-decode/delua/postprocess/ -> parents[2]
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "洛阳之战_技能脚本_解码前"
OUT = ROOT / "洛阳之战_技能脚本_解码后"
STAGING = ROOT / "delua" / "_staging_lyzz_input"

BOSS_DIRS = {str(i): f"{i}号" for i in range(1, 6)}
PAT = re.compile(r"_(\d)号_")


def main():
    if STAGING.exists():
        shutil.rmtree(STAGING)
    if OUT.exists():
        shutil.rmtree(OUT)

    for d in BOSS_DIRS.values():
        (STAGING / d).mkdir(parents=True, exist_ok=True)
        (OUT / d).mkdir(parents=True, exist_ok=True)

    bytecode, plaintext, unmatched = [], [], []

    for f in sorted(SRC.glob("*.lua")):
        m = PAT.search(f.name)
        if not m:
            unmatched.append(f.name)
            continue
        boss = BOSS_DIRS[m.group(1)]
        header = f.read_bytes()[:4]
        if header == b"\x1bLua":
            shutil.copy2(f, STAGING / boss / f.name)
            bytecode.append(f.name)
        else:
            # Already plaintext (GB2312/GBK) — normalize to UTF-8 for output
            raw = f.read_bytes()
            text = None
            for enc in ("gb2312", "gbk", "gb18030", "utf-8"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
                text = raw.decode("gbk", errors="replace")
            (OUT / boss / f.name).write_text(text, encoding="utf-8", newline="\n")
            plaintext.append(f.name)

    print(f"bytecode staged: {len(bytecode)}")
    print(f"plaintext copied: {len(plaintext)}")
    if unmatched:
        print("unmatched:", unmatched)
    for i in range(1, 6):
        d = BOSS_DIRS[str(i)]
        n_stage = len(list((STAGING / d).glob("*.lua")))
        n_plain = len(list((OUT / d).glob("*.lua")))
        print(f"{d}: staging={n_stage} plaintext_out={n_plain}")


if __name__ == "__main__":
    main()
