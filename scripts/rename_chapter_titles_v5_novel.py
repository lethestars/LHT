#!/usr/bin/env python3
"""第1–33章统一改为小说化四字章名，并重命名正文/剧情详情、更新剧情大纲。"""
from __future__ import annotations

import os
import re
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 统一规则：8–10 字小说化章名，地点/人物/情致，不堆砌肉戏动词
NOVEL_TITLES: dict[int, str] = {
    1: "新警入职体院初逢三雄",
    2: "格斗教学师徒密室交锋",
    3: "深夜审讯师徒双贯刘莽",
    4: "体院器材室蓝浩天降韩",
    5: "正副队长办公室迎新欢",
    6: "深入地牢营救师徒受辱",
    7: "韩氏休息室赵霆宇贯韩",
    8: "教师公寓雷镇岳贯韩啸",
    9: "别墅私教双胞胎轮番战",
    10: "医务室徐虎肉偿当保镖",
    11: "特警宿舍赵霆宇服罗恩",
    12: "荒野深潭沈毅惩大学生",
    13: "办公室雷镇岳反杀魏雄",
    14: "阁楼风声沈罗杰链式战",
    15: "暗巷救陆凯蓝浩天贯匪",
    16: "韩氏办公室徐虎罗恩欢",
    17: "醉酒接驾特警公寓晨炮",
    18: "露台服侍公寓双雄互攻",
    19: "雷家兄弟双龙夹击阿杰",
    20: "论坛套房赵沈夜雨双轮",
    21: "阳明山行徐虎陆凯野战",
    22: "体院私访雷宅三角交锋",
    23: "北郊送行沈毅秦烈联手",
    24: "乌龙闯北港韩氏收胡岩",
    25: "特警公寓秦烈首战阿杰",
    26: "VR隔间迷途胡岩战陆凯",
    27: "挖角之约白凡投奔体院",
    28: "消防演练浴池宿舍三战",
    29: "工地夜检严蓝韩三强战",
    30: "阳明山水潭四人链式战",
    31: "海滩潮信顾骁阳战阿杰",
    32: "空降阳明雷家弟控线起",
    33: "铁骑夜巡顾骁阳战老周",
    34: "送别夜火车严立锋战杰",
    35: "局长卧室晨曦热浪赵贯雷",
}

CHAPTER_FILE_RE = re.compile(r"^第(\d+)章(?:·(.+))?\.md$")
DETAIL_FILE_RE = re.compile(r"^第(\d+)章·(.+)剧情详情\.md$")
OUTLINE_H3_RE = re.compile(r"^(### 第(\d+)章：).+$", re.MULTILINE)


def find_chapter_file(n: int) -> str | None:
    for fn in os.listdir(BASE):
        m = CHAPTER_FILE_RE.match(fn)
        if m and int(m.group(1)) == n:
            return fn
    return None


def find_detail_file(n: int) -> str | None:
    detail_dir = os.path.join(BASE, "剧情详情")
    if not os.path.isdir(detail_dir):
        return None
    for fn in os.listdir(detail_dir):
        m = DETAIL_FILE_RE.match(fn)
        if m and int(m.group(1)) == n:
            return fn
    return None


def rename_chapters() -> list[tuple[int, str, str]]:
    log: list[tuple[int, str, str]] = []
    for n, title in sorted(NOVEL_TITLES.items()):
        old_fn = find_chapter_file(n)
        if not old_fn:
            print(f"WARN: 第{n}章正文未找到，跳过")
            continue
        new_fn = f"第{n}章·{title}.md"
        if old_fn != new_fn:
            shutil.move(os.path.join(BASE, old_fn), os.path.join(BASE, new_fn))
            log.append((n, old_fn, new_fn))
            print(f"  正文 {old_fn} -> {new_fn}")

        old_detail = find_detail_file(n)
        if old_detail:
            new_detail = f"第{n}章·{title}剧情详情.md"
            if old_detail != new_detail:
                src = os.path.join(BASE, "剧情详情", old_detail)
                dst = os.path.join(BASE, "剧情详情", new_detail)
                shutil.move(src, dst)
                print(f"  详情 {old_detail} -> {new_detail}")
                _patch_detail_header(dst, n, title)
    return log


def _patch_detail_header(path: str, n: int, title: str) -> None:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(
        r"^# 第\d+章·.+ · 剧情详情",
        f"# 第{n}章·{title} · 剧情详情",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"> 正文文件：`第\d+章·.+?\.md`",
        f"> 正文文件：`第{n}章·{title}.md`",
        text,
        count=1,
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def update_outline() -> None:
    path = os.path.join(BASE, "剧情大纲.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # 文件示例（第一节表格）
    example = NOVEL_TITLES[33]
    text = re.sub(
        r"例：`第33章·[^`]+`",
        f"例：`第33章·{example}.md`",
        text,
    )

    # 第四节速览表「章名」列（仅匹配 | N | 章名 | 篇章 | 行）
    for n, title in NOVEL_TITLES.items():
        text = re.sub(
            rf"(\| {n} \| )[^|]+( \| [A-H] \|)",
            rf"\1{title}\2",
            text,
            count=1,
        )

    # 第五节 ### 第N章：标题
    def _h3_sub(m: re.Match) -> str:
        n = int(m.group(2))
        return f"{m.group(1)}{NOVEL_TITLES.get(n, m.group(0).split('：', 1)[-1])}"

    text = OUTLINE_H3_RE.sub(_h3_sub, text)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("  已更新 剧情大纲.md")


def update_skill() -> None:
    path = os.path.join(BASE, ".cursor/skills/yangming-part3-novel/SKILL.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    example = NOVEL_TITLES[33]
    text = re.sub(
        r"`第N章·本章核心概括\.md` — \*\*直白、好懂\*\*（约 \*\*8–18 字\*\*）：只写\*\*本章主干/H 重心\*\*.*?剧情详情：`剧情详情/第N章·…剧情详情\.md`（与正文副题一致）",
        f"`第N章·章名.md` — **小说化章名**（约 **8–12 字**，全章统一；写地点/人物/情致，可不交代剧情/H 任务）。"
        f"忌直白报菜名、忌堆砌肉戏动词。例：`第33章·{example}.md`。"
        f"剧情详情：`剧情详情/第N章·…剧情详情.md`（与正文副题一致）",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"例：`第33章·[^`]+`", f"例：`第33章·{example}.md`", text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("  已更新 SKILL.md")


def main() -> None:
    print("小说化章名批量重命名 v5")
    rename_chapters()
    update_outline()
    update_skill()
    print("完成。请运行 python3 scripts/build_fullbook.py")


if __name__ == "__main__":
    main()
