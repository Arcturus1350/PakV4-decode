# postprocess — 反编译前后可选处理

主流程第 3 步的**可选**辅助脚本（非通用工具，路径常按副本约定）。

## 文件

| 文件 | 作用 |
|------|------|
| `prepare_lyzz_decode.py` | 洛阳之战：按 1–5 号首领分流；字节码进 staging，明文直写「解码后」 |
| `annotate_default_comments.py` | 对「解码后」目录中的脚本，按 Default.lua 语义补行尾注释 |

## 典型顺序

```text
skills 交付的「*_技能脚本」
  →（可选）prepare_lyzz_decode.py   # 分目录 + 只送字节码去反编译
  → delua/decompile/batch_decompile.py
  →（可选）annotate_default_comments.py
```

## 用法

脚本默认以**仓库根目录**为基准，查找/写入：

- `洛阳之战_技能脚本_解码前`
- `洛阳之战_技能脚本_解码后`
- `delua/_staging_lyzz_input`（临时）

```powershell
cd delua\postprocess
python prepare_lyzz_decode.py
# 对 staging 跑 batch_decompile 后：
python annotate_default_comments.py
```

换副本时需改脚本内目录名与首领匹配规则，或自行仿写。
