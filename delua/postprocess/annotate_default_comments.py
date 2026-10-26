# -*- coding: utf-8 -*-
"""Add Default.lua side comments to all decoded skill scripts."""
from __future__ import annotations

import re
from pathlib import Path

# repo root: .../PakV4-decode/delua/postprocess/ -> parents[2]
ROOT = Path(__file__).resolve().parents[2]
OUT = next(p for p in ROOT.iterdir() if p.is_dir() and "解码后" in p.name)

# Exact text after `--` from Default.lua / _original_path/Default.lua
PROP_COMMENTS = {
    "nNeedPoseState": "检查姿态，1为擎刀姿态，2为擎盾姿态",
    "nDamageToLifeForParty": "技能伤害给小队成员百分比回血",
    "nAttackAttenuationCof": "技能伤害渐变百分比，1024为100%，正数为增加，负数为减少。注意此参数只能在渐变类型的AOE中使用！",
    "bIgnorePrepareState": "技能是否可在吟唱中施放，吟唱、通道、蓄力技不能填true",
    "bKeyUpSkill": "为true表示keyup响应技能",
    "nCostLife": " 技能消耗生命值",
    "nCostMana": " 技能消耗的内力",
    "nCostStamina": " 技能消耗的体力",
    "nCostItemType": " 技能消耗的物品类型",
    "nCostItemIndex": " 技能消耗的物品索引ID",
    "nCostManaBasePercent": " 技能消耗的内力百分比",
    "nCostRage": " 技能消耗的怒气",
    "nCostEnergy": " 技能消耗的能量",
    "nCostSunEnergy": " 技能消耗的日能量",
    "nCostSprintPower": " 技能消耗气力值",
    "nNeedSunEnergy": " 技能释放需求日灵",
    "nNeedMoonEnergy": " 技能释放需求月魂",
    "nNeedEnergy": " 技能释放需求能量",
    "nNeedRage": " 技能释放需求怒气",
    "bIsAccumulate": " 技能是否需要聚气且消耗所有能量",
    "nNeedAccumulateCount": " 技能需要气点的个数",
    "nChainBranch": "链状技能分支数",
    "nChainDepth": "链状技能层数",
    "nMinRadius": " 技能施放的最小距离",
    "nMaxRadius": " 技能施放的最大距离",
    "bCanAddMaxRadius": " 是否受到atMaxSkillRadiusAdd魔法属性影响增加距离",
    "bCheckMinAltitude": " 是否检查最小高度",
    "nMinAltitude": "  最小高度值",
    "bCheckMaxAltitude": " 是否检查最大高度",
    "nMaxAltitude": "  最大高度值",
    "nSkillBulletType": "子弹类型(苍云为1、霸刀为3)",
    "nSkillBulletSubType": "子弹的子类型,(和BulletType一起确定不同子弹的不同表现，取值范围0~256)",
    "nAnimationPlayFrame": "延迟消失帧数，这个为发射子弹后动画等待时间,即从子弹打到目标开始算起,这么多帧之后,发送sbsEnd消息给表现.",
    "nMaxHitCount": "弹射技能的最大攻击次数",
    "nMaxHitRadius": "距离释放者的最大距离限定",
    "nMaxHoodleRadius": "弹射搜索距离",
    "nMaxSearchCount": "是否限制弹射目标(0为不限 1为只打一个目标)",
    "nProtectRadius": " 环形和矩形AOE的保护距离，范围内不受伤害",
    "nHeight": " AOE的高度，全高，圆柱体AOE中不填为2倍的nAreaRadius，矩形AOE中不填为nAreaRadius",
    "nRectWidth": " 矩形AOE的宽度，全宽，不填为nAreaRadius",
    "nCastHeight": "技能释放高度,表示释放者的合法释放高度,如果这个值为0,采用原来的skill.nHeight的释放高度规则.技能作用高度规则和原来的一样,用skill.nHeight来计算.",
    "nAngleRange": " 攻击范围的扇形角度范围",
    "nAreaRadius": " 技能作用半径",
    "nTargetCountLimit": " 技能作用目标数量限制,(小于0 代表目标数量不限制)",
    "nRectRotation": "矩形旋转角度（正数表示逆时针旋转，负数表示顺时针旋转）",
    "nRectOffset": "向量方向平移点数(正数为正向量方向，负数为反向)",
    "nPrepareFrames": " 吟唱帧数",
    "nMinPrepareFrames": " 急速效果最小吟唱帧数：默认是-1，吟唱不受急速影响。大于等于0则受急速影响，最小读条时间为填的值",
    "nChannelInterval": " 通道技间隔时间",
    "nMinChannelInterval": " 急速效果最小通道技间隔时间：默认是-1，通道不受急速影响。大于等于0则受急速影响，最通道间隔时间为填的值",
    "nChannelFrame": " 通道技持续时间，单位帧数",
    "nMinChannelFrame": " 通常配合急速最小间隔时间使用。使得通道技能整体加速。如果这个填-1，间隔不是-1，高急速可以多1跳",
    "nBulletVelocity": " 子弹速度，单位 点/帧",
    "bInstantChannel": " 通道技能是否立刻造成一次伤害",
    "bIsFormationSkill": " 是否阵眼技能",
    "nFormationRange": " 结阵的范围",
    "nLeastFormationPopulation": " 结阵的范围的最少队员数（包括队长）",
    "nTargetLifePercentMin": " 血量最小值>=",
    "nTargetLifePercentMax": " 血量最大值<=",
    "nSelfLifePercentMin": " 血量最小值>=",
    "nSelfLifePercentMax": " 血量最大值<=",
    "nBeatBackRate": " 技能被打退的概率,默认1024",
    "nBrokenRate": " 技能被打断的概率,默认1024",
    "nBreakRate": " 打断目标施法的概率,基数1024(默认是1024 100%)",
    "nDismountingRate": " 将目标击落下马几率,基数1024，默认0",
    "nWeaponDamagePercent": " 武器伤害百分比,对外功伤害有用。填0表示此次外功攻击不计算武器伤害,1024为100%",
    "dwLevelUpExp": " 升级经验",
    "nExpAddOdds": " 技能熟练度增长概率",
    "nPlayerLevelLimit": " 角色可以学会该技能所必须达到的最低等级",
}

METHOD_COMMENTS = {
    "AddSlowCheckSelfBuff": " 需求自身Buff",
    "AddSlowCheckDestBuff": " 需求目标Buff",
    "AddSlowCheckSelfOwnBuff": " 需求自身属于自己的Buff",
    "AddSlowCheckDestOwnBuff": " 需求目标属于自己的Buff",
    "AddCheckSelfLearntSkill": "检查比较Caster自己已学习的技能ID和等级",
    "SetNormalCoolDown": "技能普通CD",
    "SetCheckCoolDown": "只检查不走的CD",
}

DEPTH_COMMENTS = {
    "1": "对第一个搜索到的目标施放子技能。注意此参数只能在渐变类型的AOE中使用！",
    "2": "对第二个搜索到的目标施放子技能。",
    "3": "对第三个搜索到的目标施放子技能。",
    "4": "对第四个搜索到的目标施放子技能。",
    "5": "对第五个搜索到的目标施放子技能。",
    "6": "对第六个搜索到的目标施放子技能。",
    "7": "对第七个搜索到的目标施放子技能。",
    "8": "对第八个搜索到的目标施放子技能。",
    "9": "对第九个搜索到的目标施放子技能。",
    "10": "对第十个搜索到的目标施放子技能。",
}

BINDBUFF_COMMENTS = {
    "1": " 设置1号位Buff",
    "2": " 设置2号位Buff",
    "3": " 设置3号位Buff",
    "4": " 设置4号位Buff",
}

_prop_pat = "|".join(re.escape(k) for k in sorted(PROP_COMMENTS, key=len, reverse=True))
_method_pat = "|".join(re.escape(k) for k in sorted(METHOD_COMMENTS, key=len, reverse=True))

PROP_RE = re.compile(rf"^(.*\.)({_prop_pat})(\s*=\s*.+)$")
METHOD_RE = re.compile(rf"^(.*\.)({_method_pat})(\s*\(.*\)\s*;?\s*)$")
BINDBUFF_RE = re.compile(r"^(.*\.)BindBuff\s*\(\s*([1-4])\s*,.*\)\s*;?\s*$")
DEPTH_RE = re.compile(r"^(.*\.)SetSubSkillForAreaDepth\s*\(\s*(\d+)\s*,.*\)\s*;?\s*$")
PUBLIC_CD_RE = re.compile(r"^(.*\.)SetPublicCoolDown\s*\(\s*16\s*\)\s*;?\s*$")


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def annotate_line(line: str) -> tuple[str, bool]:
    raw = line.rstrip("\r")
    stripped = raw.lstrip()
    if not stripped or stripped.startswith("--"):
        return raw, False

    code = raw.split("--")[0].rstrip()
    existing = raw.split("--", 1)[1] if "--" in raw else None

    def finish(comment_after_dashes: str) -> tuple[str, bool]:
        if existing is not None and _norm(existing) == _norm(comment_after_dashes):
            return raw, False
        return f"{code}    --{comment_after_dashes}", True

    m = BINDBUFF_RE.match(code)
    if m:
        return finish(BINDBUFF_COMMENTS[m.group(2)])

    m = DEPTH_RE.match(code)
    if m and m.group(2) in DEPTH_COMMENTS:
        return finish(DEPTH_COMMENTS[m.group(2)])

    if PUBLIC_CD_RE.match(code):
        return finish(" 公共CD 1.5秒")

    m = PROP_RE.match(code)
    if m:
        return finish(PROP_COMMENTS[m.group(2)])

    m = METHOD_RE.match(code)
    if m:
        return finish(METHOD_COMMENTS[m.group(2)])

    return raw, False


def main() -> None:
    stats = {"files": 0, "changed_files": 0, "lines": 0}
    samples: list[tuple[str, str, str]] = []

    for path in sorted(OUT.rglob("*.lua")):
        if path.name == "Default.lua":
            continue
        stats["files"] += 1
        text = path.read_text(encoding="utf-8")
        out_lines: list[str] = []
        file_changed = 0
        for line in text.splitlines():
            new_line, did = annotate_line(line)
            if did:
                file_changed += 1
                if len(samples) < 10:
                    samples.append((path.name, line.strip(), new_line.strip()))
            out_lines.append(new_line)
        if file_changed:
            new_text = "\n".join(out_lines) + "\n"
            path.write_text(new_text, encoding="utf-8", newline="\n")
            stats["changed_files"] += 1
            stats["lines"] += file_changed

    print("OUT:", OUT)
    print("files scanned:", stats["files"])
    print("files changed:", stats["changed_files"])
    print("lines annotated:", stats["lines"])
    print("samples:")
    for name, old, new in samples:
        print(f"  [{name}]")
        print(f"    OLD: {old}")
        print(f"    NEW: {new}")

    sample = OUT / "1号" / "45462_1号_突利和顺_潜渊之刺.lua"
    print("--- sample file lines 60+ ---")
    print("\n".join(sample.read_text(encoding="utf-8").splitlines()[60:]))


if __name__ == "__main__":
    main()
