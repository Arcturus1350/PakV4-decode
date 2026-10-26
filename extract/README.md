# extract — PakV4 解包器

主流程 **第 1 步**：从客户端 PakV4 按 pathlist 抽出指定文件。

## 文件

| 文件 | 说明 |
|------|------|
| `PakV12345-Extract.exe` | 预编译解包器（须在客户端 `bin64` 下运行） |
| `main.cpp` | 解包器源码 |

## 运行要求

1. 将 exe 复制到体验服/正式服客户端的 `bin64`（与 `Engine_Lua5X64.dll` 同级）。
2. 确保能找到 Pak 根（相对 `bin64` 一般为 `..\..\PakV4`，含 `Trunk.Dir`）。
3. pathlist 文本编码使用 **GBK**（含中文路径时必须）。

用法示例（在 `bin64` 下）：

```bat
PakV12345-Extract.exe pathlist.txt
```

输出目录一般为同级的 `<exe名>.extract\`，相对路径树与 pathlist 一致。

## 与后续步骤的关系

解出 `skill.txt`、`skills.tab`、`scripts\skill\...` 后，按 [skills/](../skills/) SOP 筛副本技能并收集加密脚本，再交给 [delua/decompile/](../delua/decompile/) 反编译。
