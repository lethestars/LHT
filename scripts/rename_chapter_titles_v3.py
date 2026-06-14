#!/usr/bin/env python3
"""章名 v3：较长小说式标题，概括核心内容。"""
from __future__ import annotations

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RENAME: dict[str, str] = {
    "初来报到": "报到档案撩火·体院搜身三雄夜",
    "师徒试身": "格斗试身调教·师徒一对一实战",
    "双贯之夜": "赵归队前夜·审讯桌双贯疑犯",
    "入网收编": "器材室收网·卧底被征服入网",
    "正副迎新": "正副队长迎新·办公室交换调教",
    "断联营救": "卧底断联陷落·地牢营救师徒辱",
    "肉偿契约": "赴韩氏肉偿道谢·休息室激烈偿还",
    "挑明身份": "公寓贯穿挑明·黑帮结盟成型",
    "双胞胎夜": "私教双胞胎课·别墅轮操种马对决",
    "肉偿入队": "工地救主肉偿·新保镖入韩氏",
    "顾问初夜": "美籍顾问入境·队长宿舍彻底操服",
    "野游失控": "荒野深潭野游·副队野外暴露失控",
    "反杀收狗": "魏雄逼宫反杀·黑道大佬收为贱狗",
    "链式之夜": "外勤扑空阁楼·三明治链式三人",
    "师徒救场": "暗巷受困救场·师徒联手双贯混混",
    "双线夜事": "保镖仓库双线·办公室争夺互操",
    "醉酒接驾": "醉酒再接驾·公寓一夜至晨炮",
    "露台夜宴": "度假村露台夜·服侍群英双雄互攻",
    "兄弟言和": "兄弟言和家宴·双龙夹击招待宴",
    "同夜四轮": "论坛夜同房·四轮交锋双轮内射",
    "术后重逢": "乳粒手术定型·山林徒步再会陆凯",
    "厅长私访": "高位私访体院·验长宿舍三角局",
    "送行制裁": "离境送行制裁·汽修联手秦沈收尾",
    "乌龙闯港": "乌龙闯错地盘·会议室收编一口一后",
    "强攻首战": "特警入寓首战·公寓强攻与续战",
    "路痴邂逅": "路痴商场邂逅·隔间虚实首次交锋",
    "挖角投奔": "交流日挖角教练·胁迫后投奔阳明",
    "铁面登场": "公寓夜袭翌日·消防演练见铁面队长",
    "家法夜战": "泄密严查家法·工地夜检三人夹击",
    "四人水潭": "空降篮球天才·四人徒步链至水潭",
    "海滩偶遇": "海滩冲浪偶遇·淋浴沙滩野战失禁",
    "权力空降": "定海神针空降·阳明新局长弟控线",
    "副队秘密": "夜巡撞破副队秘密·公厕贯穿长椅盟约",
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
            print(f"mv: {fn}")

            text = open(new_path, encoding="utf-8").read()

            def h1_repl(match: re.Match) -> str:
                if match.group(2) != num:
                    return match.group(0)
                sep = "：" if "：" in match.group(1) else ":"
                return f"# 第{num}章{sep}{new_sub}"

            new_text, n = H1_RE.subn(h1_repl, text, count=1)
            if detail_suffix:
                new_text = re.sub(
                    r"^# 第\d+章·.+? · 剧情详情",
                    f"# 第{num}章·{new_sub} · 剧情详情",
                    new_text,
                    count=1,
                    flags=re.M,
                )
                new_text = re.sub(
                    r"> 正文文件：`第\d+章·[^`]+`",
                    f"> 正文文件：`第{num}章·{new_sub}.md`",
                    new_text,
                    count=1,
                )
            if new_text != text:
                open(new_path, "w", encoding="utf-8").write(new_text)


if __name__ == "__main__":
    main()
