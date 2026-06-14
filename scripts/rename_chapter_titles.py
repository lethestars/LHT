#!/usr/bin/env python3
"""一次性章名优化：重命名正文/剧情详情，更新章内 H1。"""
from __future__ import annotations

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 旧副标题（文件名中「第N章·」之后、「.md」之前）→ 新副标题
RENAME: dict[str, str] = {
    "体院402·警察搜身角色扮演三P": "体院402·新人报到夜",
    "格斗室·沈毅一对一实战贯穿阿杰": "格斗室·师徒试身",
    "审讯桌·沈阿杰双贯刘莽": "审讯桌·双贯之夜",
    "器材室·蓝浩天征服韩啸入网": "器材室·蓝爷收网",
    "办公室·赵沈正队长双颜射交换调教": "办公室·正副迎新",
    "夜色会所·断联韩啸营救": "韩氏地牢·断联营救",
    "肉偿契约·赵贯韩啸": "韩氏休息室·肉偿契约",
    "教师公寓·雷贯韩啸": "教师公寓·挑明黑帮",
    "别墅私教·阿杰陆凯双胞胎轮操": "别墅私教·双胞胎之夜",
    "工地医务室·徐虎救韩肉偿入队": "工地医务室·肉偿入队",
    "宿舍·赵霆宇操服美籍罗恩": "宿舍·美籍罗恩",
    "荒野深潭·沈毅暴露Play": "荒野深潭·野游深潭",
    "办公室·雷镇岳反杀收狗降服魏雄": "办公室·反杀收狗",
    "外勤阁楼·沈罗阿杰三明治链式": "外勤阁楼·链式之夜",
    "暗巷·蓝浩天师徒双贯救陆凯": "暗巷·师徒救场",
    "韩啸办公室·徐虎与仓库徐罗互操双线": "韩氏双线·办公室与仓库",
    "公寓·赵霆宇醉酒接驾一夜晨炮": "公寓·醉酒接驾",
    "度假村·露台魏服侍与阿杰陆凯互攻": "度假村·露台与双雄",
    "雷家·镇海镇岳兄弟双龙夹阿杰": "雷家·兄弟双龙",
    "论坛夜·韩套房4P双轮": "论坛套房·同夜四轮",
    "徐虎58吋·手术与阳明山": "阳明山·术后重逢",
    "体院雷宅·雷镇海验长私访三角夹击": "体院雷宅·厅长私访",
    "北郊汽修·沈秦联手制裁送行罗恩": "北郊汽修·送行制裁",
    "胡岩乌龙·一口一后韩啸": "韩氏会议室·胡岩乌龙",
    "特警公寓·秦烈强攻阿杰首战续战": "特警公寓·强攻首战",
    "VR隔间·胡岩迷路陆凯首战": "VR隔间·路痴邂逅",
    "交流日·白凡投奔体院": "交流日·白凡投奔",
    "消防演练·严立锋登场": "消防演练·严队登场",
    "严家法·工地严蓝韩": "工地消防·严家法",
    "白毅队长·陆凯公寓白凡": "阳明山·四人水潭",
    "海滩淋浴间·顾骁阳全裸野战双色肉钩首开": "海滩·骁阳晓杰",
    "省厅空降·雷镇海阳明局长": "省厅空降·阳明局长",
    "体育公园公厕·顾骁阳贯穿周云飞肉畜首开": "体育公园·周大哥秘密",
    # 剧情详情旧名（与正文不一致的副本）
    "私教课·别墅双胞胎": "别墅私教·双胞胎之夜",
    "正队长迎新·办公室双颜射": "办公室·正副迎新",
    "教师公寓·雷镇岳贯穿韩啸挑明黑帮": "教师公寓·挑明黑帮",
}

CHAPTER_FILE_RE = re.compile(r"^(第(\d+)章·)(.+?)(剧情详情)?\.md$")
H1_RE = re.compile(r"^(# 第(\d+)章[：:])(.+)$", re.M)


def main() -> None:
    for root, _, files in os.walk(BASE):
        if ".git" in root.split(os.sep) or "scripts" in root.split(os.sep)[-1:]:
            continue
        for fn in sorted(files):
            if not fn.endswith(".md") or not fn.startswith("第"):
                continue
            m = CHAPTER_FILE_RE.match(fn)
            if not m:
                continue
            prefix, num, subtitle, detail_suffix = m.group(1), m.group(2), m.group(3), m.group(4)
            new_sub = RENAME.get(subtitle)
            if not new_sub:
                continue
            old_path = os.path.join(root, fn)
            new_fn = f"{prefix}{new_sub}{detail_suffix or ''}.md"
            new_path = os.path.join(root, new_fn)
            if old_path == new_path:
                continue
            if os.path.exists(new_path):
                print(f"SKIP exists: {new_fn}")
                continue
            os.rename(old_path, new_path)
            print(f"mv: {fn} -> {new_fn}")

            with open(new_path, encoding="utf-8") as f:
                text = f.read()

            def h1_repl(match: re.Match) -> str:
                ch = match.group(2)
                if ch != num:
                    return match.group(0)
                sep = "：" if "：" in match.group(1) else ":"
                return f"# 第{ch}章{sep}{new_sub}"

            new_text, n = H1_RE.subn(h1_repl, text, count=1)
            if n:
                with open(new_path, "w", encoding="utf-8") as f:
                    f.write(new_text)


if __name__ == "__main__":
    main()
