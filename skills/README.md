# skills — 副本技能数据提取

本目录对应 Cursor Skill / SOP：[dungeon-skill-extract.md](dungeon-skill-extract.md)。

它**不是**「解完包之后的一小步」，而是一整套多段流程：内部会**多次调用** [extract/](../extract/) 解包器，最终产出三件套；其中第 ③ 件（加密 `.lua`）再交给 [delua/decompile/](../delua/decompile/) 反编译。

---

## 文档里到底有哪些部分

| 章节 | 内容 | 和本仓其它目录的关系 |
|------|------|----------------------|
| **交付物** | 必须齐的三件套定义 | 本步骤的验收标准 |
| **§0 环境前提** | 游戏根 / PakV4 / bin64 / 解包器路径与约束 | 解包器来自 `extract/`，须拷到 bin64 |
| **§1 心智模型** | 客户端有什么、没有什么；6 条关键事实；最短推荐链路 | 读表/找脚本的依据，避免弯路 |
| **§2 手工步骤** | Step A→B→C→D（见下表） | A/D 调 `extract`；B/C 在已解出的表上做 |
| **§3 一键脚本** | `extract_dungeon_skills.py` 用法 | 脚本若未入库，仍按 §2 手工 |
| **§4 弯路备忘** | 洛阳之战踩坑对照表 | 纯经验，不改目录 |
| **§5 可选扩展** | Represent / Buff 等表现与 Buff 表 | **非**三件套必需；需要时再解 |
| **§6 Agent 清单** | 给 Agent 复制执行的勾选列表 | 自动化执行入口 |
| **§7 编码速查** | pathlist / tab / 交付物编码 | 贯穿 A–D |

完整正文一律以 [dungeon-skill-extract.md](dungeon-skill-extract.md) 为准；本页只做索引与边界说明。

---

## §2 手工四步（skills 内部主链）

```text
Step A  解基础表          extract ← skill.txt / skills.tab / MapList.tab
Step B  全部首领技能列表   skill.txt 按 Remark 筛 → 交付物①
Step C  skills.tab 全列    按 SkillID 导 CSV    → 交付物②（机制参数在这里）
Step D  解技能脚本         extract ← ScriptFile 路径 → 交付物③（\x1bLua 字节码）
```

| Step | 输入 | 输出 | 要点 |
|------|------|------|------|
| A | pathlist（GBK） | 解包出的三张基础表 | 必须先有表，才能筛 SkillID |
| B | `skill.txt` + 首领/Remark 过滤 | `*_全部首领技能列表.txt` | 用 Remark，不要靠场景名猜 |
| C | `skills.tab` + B 的 SkillID | `*_skills.tab全列.csv` | **保留全部列**；`ScriptFile` 供 D 使用 |
| D | CSV 中的 `ScriptFile` | `{SkillID}_{Name}.lua` + `清单.txt` | 再解一次包；几乎都是字节码 |

因此：根目录「主流程」里的 `extract → skills → delua` 应理解为——

- **extract**：被 skills 的 A、D（以及可选 §5）反复使用的工具  
- **skills**：从环境到三件套的完整 SOP（上表全部章节）  
- **delua/decompile**：只消费交付物③，做反编译/格式化  

---

## 最终交付物（三件套）

| # | 典型路径 | 内容 |
|---|----------|------|
| ① | `skill_lists/{副本}_全部首领技能列表.txt` | SkillID / Level / Name / Remark |
| ② | `skill_lists/{副本}_skills.tab全列.csv` | 对应 SkillID 的 skills.tab **全部列** |
| ③ | `{副本}_技能脚本/` | 每 SkillID 一个字节码 `.lua` + `清单.txt` |

拿到 ③ 之后：

```powershell
cd delua\decompile
python batch_decompile.py <技能脚本目录> <输出目录>
```

---

## 边界（什么算 skills，什么不算）

| 算 skills | 不算 skills |
|-----------|-------------|
| 环境、过滤策略、三件套、Represent/Buff 可选扩展、Agent 清单 | Pak 解包器实现本身 → `extract/` |
| 交付物③ 的提取与校验（确认 `\x1bLua`） | 字节码 → 明文 Lua → `delua/decompile/` |
| 机制参数解读（看 CSV 列） | Default 语义注释等 → `delua/postprocess/` |
