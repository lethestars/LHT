#!/usr/bin/env python3
"""章名 v4：直白概括本章核心，不写章内铺垫段、不文绉绉。"""
from __future__ import annotations

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RENAME: dict[str, str] = {
    "报到档案撩火·体院搜身三雄夜": "体院搜身三P合欢",
    "格斗试身调教·师徒一对一实战": "格斗室师徒一对一贯穿",
    "赵归队前夜·审讯桌双贯疑犯": "审讯桌师徒双贯刘莽",
    "器材室收网·卧底被征服入网": "器材室蓝爷干服韩啸入网",
    "正副队长迎新·办公室交换调教": "办公室正副队长迎新调教",
    "卧底断联陷落·地牢营救师徒辱": "地牢救人师徒双辱",
    "赴韩氏肉偿道谢·休息室激烈偿还": "休息室赵队肉偿干韩啸",
    "公寓贯穿挑明·黑帮结盟成型": "公寓雷爷干韩啸挑明黑帮",
    "私教双胞胎课·别墅轮操种马对决": "别墅私教双胞胎轮操",
    "工地救主肉偿·新保镖入韩氏": "医务室肉偿徐虎入队",
    "美籍顾问入境·队长宿舍彻底操服": "宿舍赵队操服美籍罗恩",
    "荒野深潭野游·副队野外暴露失控": "荒野深潭干两大学生",
    "魏雄逼宫反杀·黑道大佬收为贱狗": "办公室雷爷反杀操魏雄",
    "外勤扑空阁楼·三明治链式三人": "阁楼沈罗阿杰三明治链",
    "暗巷受困救场·师徒联手双贯混混": "暗巷蓝爷师徒双贯混混",
    "保镖仓库双线·办公室争夺互操": "办公室与仓库双线互操",
    "醉酒再接驾·公寓一夜至晨炮": "公寓醉酒接驾一夜晨炮",
    "度假村露台夜·服侍群英双雄互攻": "度假村露台服侍·阿杰陆凯互攻",
    "兄弟言和家宴·双龙夹击招待宴": "雷家兄弟双龙夹阿杰",
    "论坛夜同房·四轮交锋双轮内射": "论坛套房四轮双轮内射",
    "乳粒手术定型·山林徒步再会陆凯": "阳明山徐虎术后干陆凯",
    "高位私访体院·验长宿舍三角局": "体院宿舍雷宅三角夹击",
    "离境送行制裁·汽修联手秦沈收尾": "汽修送行沈秦联手制裁",
    "乌龙闯错地盘·会议室收编一口一后": "会议室一口一后收胡岩",
    "特警入寓首战·公寓强攻与续战": "特警公寓秦烈强攻续战",
    "路痴商场邂逅·隔间虚实首次交锋": "VR隔间胡岩陆凯首战",
    "交流日挖角教练·胁迫后投奔阳明": "临时住所挖角干白凡投奔",
    "公寓夜袭翌日·消防演练见铁面队长": "消防演练浴池宿舍三线",
    "泄密严查家法·工地夜检三人夹击": "家法后工地消防三人夹击",
    "空降篮球天才·四人徒步链至水潭": "陆凯公寓白凡·阳明山四人链式水潭",
    "海滩冲浪偶遇·淋浴沙滩野战失禁": "海滩淋浴间沙滩椅野战失禁",
    "定海神针空降·阳明新局长弟控线": "警局大会空降·兄弟公寓弟控夜",
    "夜巡撞破副队秘密·公厕贯穿长椅盟约": "公厕干副队长贯穿·公寓口爆三战同床",
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
                print(f"SKIP: {new_fn}")
                continue
            os.rename(old_path, new_path)
            print(f"ok: {num}")

            text = open(new_path, encoding="utf-8").read()

            def h1_repl(match: re.Match) -> str:
                if match.group(2) != num:
                    return match.group(0)
                sep = "：" if "：" in match.group(1) else ":"
                return f"# 第{num}章{sep}{new_sub}"

            new_text, _ = H1_RE.subn(h1_repl, text, count=1)
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
