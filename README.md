# PakV4-decode

剑网3 PakV4 **技能数据提取 + Lua 反编译** 工具链。

forked from [jx3pak/PakV4-Extract](https://github.com/jx3pak/PakV4-Extract)

---

#### 大人，时代变了


---

## 目录作用

| 目录 | 角色 |
|------|------|
| [extract/](extract/) | **解包工具**：按 pathlist 从 PakV4 抽文件（被 skills 多次调用） |
| [skills/](skills/) | **完整提取 SOP**：环境 → 心智模型 → 解表/筛列表/导 CSV/解脚本 → 三件套（内含多段，见下） |
| [delua/decompile/](delua/decompile/) | **反编译工具**：只处理 skills 交付物③（加密 `.lua`）→ 可读源码 |

```text
                    ┌─ Step A：解基础表 ─────────────┐
extract/  ◄─────────┤                               │
                    └─ Step D：按 ScriptFile 解脚本 ─┤
                                                    ▼
skills/  SOP 多段 ──► ①技能列表  ②skills.tab CSV  ③加密.lua
                                                    │
                                                    ▼
delua/decompile/  ◄──── 仅消费 ③，反编译 + 格式化
        │（可选）
        ▼
delua/postprocess/  分目录 / Default 注释
```

---

## skills 内部有多段（不要当成单步）

详情与索引见 [skills/README.md](skills/README.md)，正文 SOP 见 [skills/dungeon-skill-extract.md](skills/dungeon-skill-extract.md)：

| 部分 | 做什么 |
|------|--------|
| §0 环境 | 游戏根、bin64、解包器、GBK pathlist |
| §1 心智模型 | 客户端有/没有什么、关键事实、最短链路 |
| §2 Step A–D | 解表 → 技能列表 → 全列 CSV → 加密脚本 |
| §3 一键脚本 | `extract_dungeon_skills.py`（若可用） |
| §4 弯路 | 洛阳之战踩坑，下次别做 |
| §5 可选扩展 | Represent / Buff（非三件套必需） |
| §6 Agent 清单 | 复制即用的执行勾选 |
| §7 编码速查 | pathlist / tab / 交付物编码 |

日常用法：先按 **skills** 跑通三件套，再对 ③ 跑 **delua/decompile**。

---

## 目录一览

```
PakV4-decode/
├── extract/       # PakV4 解包器（源码 + exe）—— skills 的执行器
├── skills/        # 副本技能提取 SOP（多段，产出三件套）
├── delua/            # 后处理工具集
│   ├── decompile/     # ★ 对交付物③反编译
│   ├── luac-parser-rs/# 可选元信息
│   ├── postprocess/   # 可选：分目录 / 注释
│   ├── jx3dat/        # 旁路
│   └── utils/         # 旁路
└── samples/       # 样例数据（非工具）
```

工作数据（`input/`、`output/`、`skill_lists/`、`*_技能脚本*` 等）放在仓库根或临时目录，**不要**长期堆进工具子目录。旁路约定见 [delua/README.md](delua/README.md)。
