# utils — 通用小工具（旁路）

与解包 / 技能提取 / 反编译主链路弱相关的辅助脚本。

## 文件

| 文件 | 作用 |
|------|------|
| `process_filenames.py` | 读取目录下文件名，按 `_` 拆分后保留第 3 段，去重写入文本 |

## 用法

```powershell
python process_filenames.py <文件夹路径> [输出文件名]
# 默认输出：output.txt
```

示例：`a_b_c_d.lua` → 提取 `c`。
