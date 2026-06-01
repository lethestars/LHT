#!/usr/bin/env python3
"""校验第三部 canon 文档与章节文件是否基本同步。"""
from __future__ import annotations

import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTER_RE = re.compile(r"^第(\d+)章·(.+)\.md$")
OUTLINE = os.path.join(BASE, "剧情大纲.md")
CHARS = os.path.join(BASE, "人物设定.md")
REGISTRY = os.path.join(
    BASE, ".cursor/skills/yangming-part3-novel/canon-registry.md"
)


def discover_chapters() -> dict[int, str]:
    found: dict[int, str] = {}
    for fn in os.listdir(BASE):
        m = CHAPTER_RE.match(fn)
        if m:
            found[int(m.group(1))] = fn
    return found


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def main() -> int:
    chapters = discover_chapters()
    if not chapters:
        print("WARN: 未发现 第N章·….md 正文")
        return 1

    max_ch = max(chapters)
    print(f"正文文件: 第1–{max_ch}章 共 {len(chapters)} 篇")

    missing = [n for n in range(1, max_ch + 1) if n not in chapters]
    if missing:
        print(f"WARN: 缺章号文件: {missing}")

    outline = read(OUTLINE)
    for n in range(1, max_ch + 1):
        if f"| {n} |" not in outline and f"第{n}章" not in outline:
            print(f"WARN: 剧情大纲.md 可能缺第{n}章速览")

    if os.path.isfile(REGISTRY):
        reg = read(REGISTRY)
        m = re.search(r"最新定稿正文\s*\|\s*第\s*(\d+)\s*章", reg)
        if m:
            reg_ch = int(m.group(1))
            if reg_ch != max_ch:
                print(
                    f"WARN: canon-registry 登记第{reg_ch}章，"
                    f"但正文最大为第{max_ch}章 — 请更新登记册"
                )
        else:
            print("WARN: canon-registry 未找到「最新定稿正文」行")
    else:
        print("WARN: 缺少 canon-registry.md")

    chars = read(CHARS)
    if "15人平等主角团" not in chars and "15人" not in chars:
        print("WARN: 人物设定.md 主角团人数描述可能过时")

    if "截至第29章" in chars or "截至第26章" in chars:
        print("WARN: 人物设定 关系索引「截至第N章」可能未更新到最新正文")

    print("OK: 基础校验完成（详见 WARN）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
