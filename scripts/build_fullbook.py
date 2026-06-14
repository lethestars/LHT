#!/usr/bin/env python3
"""合并第1–N章正文与番外，生成全本整合 md/txt/epub。"""
from __future__ import annotations

import os
import re
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTER_RE = re.compile(r"^第(\d+)章·(.+)\.md$")
OUT_MD = os.path.join(BASE, "阳明宇宙·第三部·全本整合.md")
OUT_TXT = os.path.join(BASE, "阳明宇宙·第三部·全本整合.txt")
OUT_EPUB = os.path.join(BASE, "阳明宇宙·第三部·全本整合.epub")
EXTRAS = ["番外1：赵霆宇·角色扮演.md", "番外2：阿杰·篮球场.md"]


def discover_chapters() -> list[tuple[int, str]]:
    found: dict[int, str] = {}
    for fn in os.listdir(BASE):
        m = CHAPTER_RE.match(fn)
        if m:
            found[int(m.group(1))] = os.path.join(BASE, fn)
    if not found:
        # 兼容旧文件名 第N章.md
        for fn in os.listdir(BASE):
            m = re.match(r"^第(\d+)章\.md$", fn)
            if m:
                found[int(m.group(1))] = os.path.join(BASE, fn)
    return [(n, found[n]) for n in sorted(found)]


def load_chapter(n: int, path: str) -> str:
    """从文件名注入统一章标题，并剔除正文内旧式标题行。"""
    with open(path, encoding="utf-8") as f:
        body = f.read().strip()
    m = CHAPTER_RE.match(os.path.basename(path))
    subtitle = m.group(2) if m else ""
    body = re.sub(r"^#\s*第\d+章[：·][^\n]+\n+", "", body, count=1)
    return f"# 第{n}章·{subtitle}\n\n{body}"


def build_epub(md_path: str, epub_path: str) -> None:
    pandoc = shutil.which("pandoc") or os.path.join(BASE, ".tools", "pandoc", "pandoc")
    args = ["--toc", "--toc-depth=2", "--metadata", "title=阳明宇宙·第三部"]
    try:
        import pypandoc

        if os.path.isfile(pandoc):
            os.environ["PYPANDOC_PANDOC"] = pandoc
        pypandoc.convert_file(md_path, "epub", outputfile=epub_path, extra_args=args)
    except Exception:
        if os.path.isfile(pandoc):
            import subprocess

            subprocess.run([pandoc, md_path, "-o", epub_path, *args], check=True)
        else:
            raise


def main() -> int:
    parts: list[str] = []
    chapters = discover_chapters()
    if not chapters:
        print("未找到章节文件（期望：第N章·副标题.md）", file=sys.stderr)
        return 1

    for n, path in chapters:
        parts.append(load_chapter(n, path))
        print(f"  + 第{n}章 ({os.path.basename(path)})")

    for name in EXTRAS:
        path = os.path.join(BASE, name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                parts.append(f.read().strip())
            print(f"  + {name}")

    full = "\n\n".join(parts) + "\n"
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(full)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(full)

    print(f"写入 {OUT_MD} ({len(chapters)} 章)")
    try:
        build_epub(OUT_MD, OUT_EPUB)
        print(f"写入 {OUT_EPUB}")
    except Exception as e:
        print(f"epub 跳过: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
