---
name: jx3-dungeon-skill-extract
description: >-
  从剑网3体验服(JX3_EXP) PakV4 提取副本首领技能三件套：全部首领技能列表、
  skills.tab 全列 CSV、每 SkillID 一个技能脚本(.lua 字节码)。
  在用户要求提取某副本技能/SkillID/skills.tab/技能脚本时使用。
---

# JX3 副本技能数据提取（SOP）

目标：对任意副本，用尽量少的步骤拿到与「洛阳之战」同构的三件交付物。

> 本文件是一份**多段** SOP（环境 / 心智模型 / 手工 A–D / 一键 / 弯路 / 可选扩展 / Agent 清单 / 编码），不是「只解脚本」的单步说明。  
> 章节索引与和 `extract/`、`delua/` 的边界见同目录 [README.md](README.md)。

## 最终交付物（必须齐）

以副本名 `{副本}` 为例（洛阳之战已验证）：

| # | 路径 | 内容 |
|---|------|------|
| 1 | `skill_lists/{副本}_全部首领技能列表.txt` | 从 UI `skill.txt` 筛出的 SkillID/Level/Name/Remark |
| 2 | `skill_lists/{副本}_skills.tab全列.csv` | `skills.tab` 中对应 SkillID 的**全部列** |
| 3 | `{副本}_技能脚本/` | 每 SkillID 一个文件：`{SkillID}_{SkillName}.lua` + `清单.txt` |

参考成品（勿删，作对照）：

- `PakV4-Extract/skill_lists/洛阳之战_全部首领技能列表.txt`
- `PakV4-Extract/skill_lists/洛阳之战_skills.tab全列.csv`
- `PakV4-Extract/洛阳之战_技能脚本/`

---

## 0. 环境前提（一次配好）

| 项 | 典型路径 |
|----|----------|
| 游戏根 | `E:\JX3_EXP` |
| PakV4 | `E:\JX3_EXP\Pakv4`（含 `Trunk.dir`） |
| 客户端 bin64 | `E:\JX3_EXP\bin\zhcn_exp\bin64` |
| 解包器 | 本仓 [`extract/PakV12345-Extract.exe`](../extract/)（复制到 bin64 后运行） |

约束：

- **不要改** `E:\JX3_EXP` 游戏文件；只读解包。
- 解包器必须在 **bin64** 下运行，才能找到 `..\..\Pakv4`。
- pathlist 文件编码用 **GBK**（中文路径）。
- 副本名当**整词**匹配（如「洛阳之战」），不要拆字。

拿到技能脚本（字节码）后，下一步用 [`delua/decompile`](../delua/decompile/) 反编译并格式化，见仓库根 `README.md`。

一键脚本（若已有 `extract_dungeon_skills.py`）：

```bat
python scripts\extract_dungeon_skills.py --dungeon 洛阳之战 --remark-substr "突利和顺,田承嗣,伊曼,阿史那承庆,史朝义"
```

换副本时改 `--dungeon` 与 `--remark-substr` / `--remark-regex` 即可。

---

## 1. 先建立正确心智模型（避免走弯路）

### 有 / 没有

| 有（客户端 Pak） | 没有（通常服务端） |
|------------------|-------------------|
| `ui\Scheme\Case\skill.txt`（UI 名/Remark） | `scripts\Map\{副本}\include\*技能数据.lua` |
| `settings\skill\skills.tab`（机制主表） | 按 MapID 单独拆的技能包 |
| `scripts\skill\<ScriptFile>`（单技能施放脚本） | 明文可读的 boss AI 总控 |
| `Represent\skill\*`（表现，可选） | |

### 关键事实

1. **多难度共用 SkillID**：`MapList.tab` 里 10 人/25 普/25 英常指向同一 `jsonmap`，技能表一般**不按难度拆表**；难度差靠不同 SkillID 命名（如 `25PT`/`25YX`）或服务端分支。
2. **`skills.tab` 不是「副本清单」**：是全游戏技能主数据（约百列）。副本技能是其中按 SkillID 筛出的子集。
3. **机制参数在表里，不在脚本文件名里**：目标关系、`IsChannelSkill`、`ScriptFile`、`SkillCoefficient`/`AOE`/`SkillEventMask*` 等 → 全在 `skills.tab` 行内。
4. **技能脚本扩展名 `.lua`，内容是字节码**：文件头 `\x1bLua`。能提取、能对照 SkillID，但不是明文源码。
5. **`NpcTemplate` 的 SkillID1..8 槽**对首领机制技常常是空的；不要指望靠 npcid 反查全套技能。
6. **场景 `*.jsonmap` / preload** 不是技能数据库，最多有模型/动画预加载。

### 推荐链路（最短）

```
MapList.tab 确认副本名
    → ui/Scheme/Case/skill.txt 按 Remark 筛 SkillID   → 交付物①
    → settings/skill/skills.tab 按 SkillID 导全列     → 交付物②
    → ScriptFile → scripts/skill/.../*.lua 解包扁平化 → 交付物③
```

---

## 2. 手工步骤（脚本不可用时）

### Step A — 解基础表

对 `extract/PakV12345-Extract.exe`（已复制到 bin64）喂 GBK pathlist：

```
ui\Scheme\Case\skill.txt
settings\skill\skills.tab
settings\MapList.tab
```

输出目录一般是：

`E:\JX3_EXP\bin\zhcn_exp\bin64\PakV12345-Extract.extract\`

### Step B — 做「全部首领技能列表」

1. 打开 `ui\Scheme\Case\skill.txt`（可能是 UTF-8 或 GBK）。
2. 用 **Remark** 过滤，不要用场景名瞎猜文件。
3. 洛阳之战验证过的 Remark 形态：

   `(45462) 1号_突利和顺_潜渊之刺`

4. 过滤策略（按可用性选）：
   - **按首领子串**：`突利和顺,田承嗣,伊曼,阿史那承庆,史朝义`
   - **按编号**：正则 `\d+号_`
   - **按副本名**：Remark/`SkillName` 含 `{副本}`（部分本有效）

5. 写出 `skill_lists/{副本}_全部首领技能列表.txt`，建议格式：

```text
# {副本} · 全部首领技能列表
# 来源: 客户端 ui/Scheme/Case/skill.txt
# 字段: SkillID / Level / Name / Remark

## 1号_xxx
SkillID	Level	Name	Remark
...
```

### Step C — 导 `skills.tab` 全列 CSV

1. `settings\skill\skills.tab` **用 GBK 读**。
2. 以 Step B 的 SkillID 集合过滤。
3. **保留全部列**（不要只抽几列），UTF-8 BOM CSV，便于 Excel。
4. 输出：`skill_lists/{副本}_skills.tab全列.csv`

必看列（机制参数所在处）：

- `SkillID`, `SkillName`, `MaxLevel`, `KindType`, `CastMode`
- `IsChannelSkill`, `UseCastScript`, `ScriptFile`
- `TargetType*`, `TargetRelation*`
- `AOE`, `LongRange`
- `SkillCoefficient`, `DotCoefficient`, `SurplusCoefficient`
- `SkillEventMask1/2/3`, `MapBanMask`

### Step D — 按 ScriptFile 解技能脚本

1. 从 CSV/`skills.tab` 取每行 `ScriptFile`（相对 `scripts\skill\`）。
2. 例：`npc\副本BOSS\洛阳之战\1号_突利和顺\1号_突利和顺_浊浪登天.lua`
3. pathlist 写成：

```
scripts\skill\npc\副本BOSS\洛阳之战\...\xxx.lua
scripts\skill\Default.lua
```

4. 解包后复制到 `{副本}_技能脚本\`：
   - 扁平：`{SkillID}_{SkillName}.lua`（**一技能一文件**）
   - 附 `清单.txt`：`SkillID ↔ ScriptFile ↔ 本地文件名`
   - 可选保留 `_original_path\` 原相对路径树

5. 校验：几乎全部文件头应为 `b'\x1bLua'`；`Default.lua` 可能是明文/另一格式。

---

## 3. 一键脚本用法

脚本：`PakV4-Extract/scripts/extract_dungeon_skills.py`

```bat
:: 按首领名子串（最稳）
python scripts\extract_dungeon_skills.py --dungeon 某副本 --remark-substr "首领A,首领B,首领C"

:: 按正则
python scripts\extract_dungeon_skills.py --dungeon 某副本 --remark-regex "\d+号_"

:: 自定义输出根目录
python scripts\extract_dungeon_skills.py --dungeon 某副本 --remark-substr "首领A" --out D:\out
```

成功时 stdout 末尾打印三行路径。若 `matched_rows=0`：先手工打开 `skill.txt` 搜首领名，确认 Remark 真实字符串后再改过滤条件。

---

## 4. 洛阳之战走过的弯路（下次不要再做）

| 弯路 | 为什么浪费时间 | 正确做法 |
|------|----------------|----------|
| 找 `scripts\Map\洛阳之战\*技能数据.lua` | 不在客户端 Pak | 用 `skills.tab` → `scripts\skill\...` |
| 在 `jsonmap`/entities 里找 SkillID | 场景美术摆放，无战斗 ID | 只看 skill 表 |
| 用 `NpcTemplate` Skill 槽反查 | 首领机制技常不挂槽 | 以 UI Remark / skills.tab 为准 |
| 以为 Represent 覆盖全部技能 | 多数只有普攻有 caster 行 | Represent 当可选附加 |
| 按 MapID 835 找独立技能包 | 三难度共用 SkillID | 一份列表覆盖三难度 |
| 把 `.lua` 当明文打开 | `\x1bLua` 字节码 | 接受二进制；参数看 CSV |

---

## 5. 可选扩展（非三件套必需）

需要表现/Buff 时再解：

```
Represent\skill\skill_caster_npc.txt
Represent\skill\skill_missile.txt
Represent\skill\skill_effect.txt
Represent\skill\skill_buff.txt
ui\Scheme\Case\Buff.txt
settings\skill\Buff.tab
```

关联键：`SkillID` / `RepresentID` / `BuffID`（BuffID 偶发出现在 UI/表现交叉里，不要对全表模糊扫名）。

---

## 6. Agent 执行清单（复制即用）

对新副本 `{副本}`：

1. [ ] 确认 `PakV12345-Extract.exe` 在 bin64，`Pakv4\Trunk.dir` 存在  
2. [ ] 向用户确认首领名或 Remark 过滤方式（子串 / 正则）  
3. [ ] 跑 `scripts/extract_dungeon_skills.py` **或** 按 Step A–D 手工做完  
4. [ ] 验收三件套路径存在且 SkillID 数量一致（列表唯一 ID ≈ CSV 行数 ≈ 脚本文件数；`Default.lua` 共享会导致脚本物理文件略少，但扁平复制仍应按 SkillID 出满）  
5. [ ] 抽查 CSV 含 `ScriptFile`/`CastMode`/`SkillCoefficient`/`AOE`/`SkillEventMask1`  
6. [ ] 抽查脚本文件头 `\x1bLua`  
7. [ ] 用中文简要回复三件路径 + 技能数量；不默认再解 Represent/Map 脚本  

---

## 7. 编码速查

| 文件 | 编码 |
|------|------|
| pathlist for extractor | GBK |
| `settings\skill\skills.tab` | GBK |
| `ui\Scheme\Case\skill.txt` | 常见 UTF-8，失败再试 GBK |
| 交付物 txt/csv | UTF-8（CSV 用 utf-8-sig） |

