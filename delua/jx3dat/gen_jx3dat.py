#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 JX3 语音包 .jx3dat（仅填充 BUFF/DEBUFF/CASTING 其一）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TYPE_MAP = {
    1: "BUFF",
    2: "DEBUFF",
    3: "CASTING",
}

# 与 cast1.jx3dat 保持一致的键顺序
SECTION_ORDER = (
    "BUFF",
    "CHAT",
    "CASTING",
    "TALK",
    "NPC",
    "DEBUFF",
    "__meta",
    "DOODAD",
)

META_BLOCK = """\t__meta = {
\t\tszServer = "qwq",
\t\tszAuthor = "qwq",
\t\tszCustomVoicePacketUUID = "",
\t\tszLang = "zhcn",
\t\tnTimeStamp = 1791989207,
\t\tszOfficialVoicePacketUUID = "",
\t\tszEdition = "zhcn_hd",
\t},"""

ENCODING = "gbk"  # GB2312 超集，兼容中文作者名

HELP_EPILOG = """
说明:
  按类型只填充对应板块（BUFF / DEBUFF / CASTING），在指定地图编号下
  生成 dwID 从头到尾（含两端）的全部条目，每条 nLevel=1。
  其余板块置空，仅保留 __meta。输出文件编码为 GBK（兼容 GB2312）。

类型:
  1  BUFF
  2  DEBUFF
  3  CASTING

参数格式:
  <类型> [地图编号] <dwID头> <dwID尾>
  地图编号可省略，省略时默认 836。

示例:
  python gen_jx3dat.py 1 332 17596 17599
      生成 BUFF，地图 332，dwID 17596~17599（等同 cast1.jx3dat）

  python gen_jx3dat.py 3 9004 9010
      生成 CASTING，地图默认 836，dwID 9004~9010

  python gen_jx3dat.py 2 836 17801 17805 -o my.jx3dat
      生成 DEBUFF，地图 836，dwID 17801~17805，输出为 my.jx3dat

默认输出文件名:
  <类型名>_<地图编号>_<dwID头>-<dwID尾>.jx3dat
  例如: BUFF_332_17596-17599.jx3dat
""".strip()


def build_entries(start_id: int, end_id: int) -> str:
    chunks = []
    for dw_id in range(start_id, end_id + 1):
        chunks.append(
            "\t\t\t{\n"
            "\t\t\t\tnLevel = 1,\n"
            f"\t\t\t\tdwID = {dw_id},\n"
            "\t\t\t},"
        )
    return "\n".join(chunks)


def build_section(name: str, map_id: int, start_id: int, end_id: int) -> str:
    entries = build_entries(start_id, end_id)
    return (
        f"\t{name} = {{\n"
        f"\t\t[{map_id}] = {{\n"
        f"{entries}\n"
        f"\t\t}},\n"
        f"\t}},"
    )


def generate(kind: int, map_id: int, start_id: int, end_id: int) -> str:
    active = TYPE_MAP[kind]
    lines = ["return {"]
    for key in SECTION_ORDER:
        if key == "__meta":
            lines.append(META_BLOCK)
        elif key == active:
            lines.append(build_section(key, map_id, start_id, end_id))
        else:
            lines.append(f"\t{key} = {{}},")
    lines.append("}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gen_jx3dat.py",
        description="生成仅含 BUFF/DEBUFF/CASTING 之一的 jx3dat 语音包文件。",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "type",
        type=int,
        choices=[1, 2, 3],
        metavar="类型",
        help="板块类型：1=BUFF，2=DEBUFF，3=CASTING",
    )
    parser.add_argument(
        "args",
        nargs="+",
        metavar="参数",
        help="[地图编号] dwID头 dwID尾；地图编号省略时默认 836",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="文件名",
        help="输出文件名（默认按类型与区间自动命名）",
    )
    ns = parser.parse_args(argv)

    nums = ns.args
    if len(nums) == 2:
        map_id = 836
        start_id, end_id = int(nums[0]), int(nums[1])
    elif len(nums) == 3:
        map_id = int(nums[0])
        start_id, end_id = int(nums[1]), int(nums[2])
    else:
        parser.error("参数应为: <类型> [地图编号] <dwID头> <dwID尾>（详见 -h）")

    if start_id > end_id:
        parser.error(f"dwID头({start_id}) 不能大于 dwID尾({end_id})")

    ns.map_id = map_id
    ns.start_id = start_id
    ns.end_id = end_id
    return ns


def default_filename(kind: int, map_id: int, start_id: int, end_id: int) -> str:
    return f"{TYPE_MAP[kind]}_{map_id}_{start_id}-{end_id}.jx3dat"


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    content = generate(ns.type, ns.map_id, ns.start_id, ns.end_id)
    out = Path(ns.output or default_filename(ns.type, ns.map_id, ns.start_id, ns.end_id))
    out.write_bytes(content.encode(ENCODING))
    count = ns.end_id - ns.start_id + 1
    print(
        f"已生成 {out.name} | {TYPE_MAP[ns.type]} 地图[{ns.map_id}] "
        f"dwID {ns.start_id}-{ns.end_id} 共 {count} 条 | 编码 {ENCODING}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
