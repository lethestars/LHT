#!/usr/bin/env python3
"""章名 v2：单一小说式主标题，不含地点/人名。"""
from __future__ import annotations

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 当前文件名中「第N章·」之后到「.md」之前的完整副标题 → 新主标题
RENAME: dict[str, str] = {
    "体院402·新人报到夜": "初来报到",
    "格斗室·师徒试身": "师徒试身",
    "审讯桌·双贯之夜": "双贯之夜",
    "器材室·蓝爷收网": "入网收编",
    "办公室·正副迎新": "正副迎新",
    "韩氏地牢·断联营救": "断联营救",
    "韩氏休息室·肉偿契约": "肉偿契约",
    "教师公寓·挑明黑帮": "挑明身份",
    "别墅私教·双胞胎之夜": "双胞胎夜",
    "工地医务室·肉偿入队": "肉偿入队",
    "宿舍·美籍罗恩": "顾问初夜",
    "荒野深潭·野游深潭": "野游失控",
    "办公室·反杀收狗": "反杀收狗",
    "外勤阁楼·链式之夜": "链式之夜",
    "暗巷·师徒救场": "师徒救场",
    "韩氏双线·办公室与仓库": "双线夜事",
    "公寓·醉酒接驾": "醉酒接驾",
    "度假村·露台与双雄": "露台夜宴",
    "雷家·兄弟双龙": "兄弟言和",
    "论坛套房·同夜四轮": "同夜四轮",
    "阳明山·术后重逢": "术后重逢",
    "体院雷宅·厅长私访": "厅长私访",
    "北郊汽修·送行制裁": "送行制裁",
    "韩氏会议室·胡岩乌龙": "乌龙闯港",
    "特警公寓·强攻首战": "强攻首战",
    "VR隔间·路痴邂逅": "路痴邂逅",
    "交流日·白凡投奔": "挖角投奔",
    "消防演练·严队登场": "铁面登场",
    "工地消防·严家法": "家法夜战",
    "阳明山·四人水潭": "四人水潭",
    "海滩·骁阳晓杰": "海滩偶遇",
    "省厅空降·阳明局长": "权力空降",
    "体育公园·周大哥秘密": "副队秘密",
}

CHAPTER_FILE_RE = re.compile(r"^第(\d+)章·(.+?)(剧情详情)?\.md$")
H1_RE = re.compile(r"^(# 第(\d+)章[：:])(.+)$", re.M)


def main() -> None:
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in (".git", "scripts", "node_modules")]
        for fn in sorted(files):
            m = CHAPTER_FILE_RE.match(fn)
            if not m:
                continue
            num, subtitle, detail_suffix = m.group(1), m.group(2), m.group(3)
            new_sub = RENAME.get(subtitle)
            if not new_sub:
                continue
            old_path = os.path.join(root, fn)
            new_fn = f"第{num}章·{new_sub}{detail_suffix or ''}.md"
            new_path = os.path.join(root, new_fn)
            if old_path == new_path:
                continue
            if os.path.exists(new_path):
                print(f"SKIP exists: {new_fn}")
                continue
            os.rename(old_path, new_path)
            print(f"mv: {fn} -> {new_fn}")

            text = open(new_path, encoding="utf-8").read()

            def h1_repl(match: re.Match) -> str:
                if match.group(2) != num:
                    return match.group(0)
                sep = "：" if "：" in match.group(1) else ":"
                return f"# 第{num}章{sep}{new_sub}"

            new_text, n = H1_RE.subn(h1_repl, text, count=1)
            if n:
                open(new_path, "w", encoding="utf-8").write(new_text)

            # 剧情详情首行
            if detail_suffix:
                t2 = re.sub(
                    r"^# 第\d+章·.+? · 剧情详情",
                    f"# 第{num}章·{new_sub} · 剧情详情",
                    new_text,
                    count=1,
                    flags=re.M,
                )
                if t2 != new_text:
                    open(new_path, "w", encoding="utf-8").write(t2)


if __name__ == "__main__":
    main()
