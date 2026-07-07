#!/usr/bin/env python3
"""第1–33章统一改为小说化四字章名，并重命名正文/剧情详情、更新剧情大纲。"""
from __future__ import annotations

import os
import re
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 统一规则：8–10 字小说化章名，地点/人物/情致，不堆砌肉戏动词
NOVEL_TITLES: dict[int, str] = {
    1: "新警入职：体院宿舍初遇三猛男",
    2: "格斗教学：格斗室里师徒一对一交锋",
    3: "深夜审讯：审讯桌上师徒双贯刘莽",
    4: "器材室征服：蓝浩天干服桀骜韩啸",
    5: "正副队长迎新：办公室里的双重颜射",
    6: "深入地牢营救：师徒双双沦陷受辱之夜",
    7: "休息室的肉偿：赵霆宇贯穿韩啸道谢",
    8: "教师公寓密盟：雷镇岳贯穿韩啸挑明黑帮",
    9: "别墅私教单：阿杰与陆凯双操双胞胎",
    10: "医务室的谢恩：徐虎肉偿韩啸当保镖",
    11: "特警宿舍征服：赵队操服洋客罗恩",
    12: "荒野深潭暴露：沈毅惩治两名大学生",
    13: "办公室反杀：雷镇岳将魏雄训成骚狗",
    14: "阁楼风声：沈毅、罗恩与阿杰的三明治链式",
    15: "暗巷救场：蓝浩天与陆凯师徒双贯混混",
    16: "韩氏办公室与仓库：徐虎与罗恩的双线互操",
    17: "醉酒接驾：特警公寓的一夜暴操与晨炮",
    18: "度假村露台与公寓：魏雄服侍蓝雷与阿杰陆凯互攻",
    19: "雷家兄弟和解：双龙夹击阿杰的极致快感",
    20: "论坛套房夜雨：赵沈套房4P双轮内射",
    21: "阳明山行：徐虎术后与陆凯的别墅野战",
    22: "体院私访：雷镇海、蓝浩天与雷镇岳的三角酒局",
    23: "北郊送行：罗恩离境与沈毅秦烈的汽修厂同欢",
    24: "乌龙闯北港：韩啸会议室一口一后收编胡岩",
    25: "特警公寓新丁：秦烈搬家与阿杰的公寓首战",
    26: "VR隔间的迷途：胡岩与陆凯的虚拟幻境首战",
    27: "挖角之约：白凡受胁迫投奔体院",
    28: "消防演练：浴池与宿舍里的特警消防大混战",
    29: "工地夜检：严立锋、蓝浩天与韩啸的三人强战",
    30: "阳明山水潭链式：徐胡陆白四人野外精液铺地",
    31: "海滩潮信：顾骁阳与阿杰的沙滩椅干到失禁",
    32: "空降阳明：雷镇海宣布任职与雷家兄弟弟控线",
    33: "铁骑夜巡：顾骁阳与周云飞的公厕摩托三战",
    34: "送别夜火车：严立锋与阿杰的软卧火车偷吃",
    35: "局长卧室的晨曦：雷家兄弟晨炮与赵队办公室贯雷局",
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
