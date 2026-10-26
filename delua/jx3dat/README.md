# jx3dat — JX3 数据文件处理（旁路）

与主流程（解包技能 → 反编译）**无关**的 `.jx3dat` 生成、裁剪与比对工具。

## 文件

| 文件 | 作用 |
|------|------|
| `gen_jx3dat.py` | CLI：生成仅含 BUFF / DEBUFF / CASTING 之一的语音包 jx3dat（GBK） |
| `generate_jx3dat.py` | 交互式：生成 CASTING/NPC 等模板（UTF-8） |
| `get_723.py` | 每个二级结构内只保留 `[723]` 块 |
| `process_ntime.py` | `nTime` 含 `;` 时只保留第一段 |
| `compare_binary_files.py` | 按固定子目录映射比较 `new/` 与 `old/` |

## 用法示例

```powershell
# CLI 语音包（推荐）
python gen_jx3dat.py 1 332 17596 17599
python gen_jx3dat.py 3 9004 9010 -o my.jx3dat
python gen_jx3dat.py -h

# 交互生成
python generate_jx3dat.py

# 以下脚本路径多写在 main 内，使用前按需修改
python get_723.py
python process_ntime.py
python compare_binary_files.py
```

输入与结果请放在仓库根临时目录或 [samples/](../../samples/) 之外的工作区；本目录只保留工具。
