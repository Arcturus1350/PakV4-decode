# decompile — Lua 字节码反编译

主流程 **第 3 步**：基于 `unluac.jar` 批量反编译技能脚本字节码，并格式化为更易读的 Lua。

## 文件

| 文件 | 作用 |
|------|------|
| `batch_decompile.py` | 入口：unluac → 可选元信息 → 自动格式化 |
| `format_unluac_enhanced.py` | 增强格式化（可读 `luac-parser-rs` 的 metadata） |
| `format_unluac_output.py` | 基础格式化 |
| `unluac.jar` | Lua 5.1 字节码反编译器 |

## 依赖

- Python 3.x  
- Java Runtime（`java -jar unluac.jar`）  
- 可选：Rust / Cargo（[`../luac-parser-rs`](../luac-parser-rs/)，无则自动跳过元信息）

---

## 批量解码（推荐）

### 1. 准备目录

在仓库根目录创建临时目录（名称可改）：

```
PakV4-decode/
├── input/          ← 第 2 步产出的字节码 .lua
├── output/         ← 解码结果
└── delua/decompile/   ← 本目录
```

### 2. 执行

```powershell
cd delua\decompile
python batch_decompile.py ..\..\input ..\..\output
```

| 参数 | 含义 |
|------|------|
| 第 1 个 | 源目录（字节码） |
| 第 2 个 | 输出目录（明文）；**务必指定**，否则会覆盖源文件 |

脚本递归处理源目录下所有 `.lua`，并在输出中保持相对路径。

### 3. 结果

- 成功：`output\` 下对应相对路径  
- 失败列表：`output\decompile_errors.txt`

---

## 其他用法

只格式化已解码文本：

```powershell
python format_unluac_enhanced.py decoded.lua decoded.lua
# 或
python format_unluac_output.py decoded.lua decoded.lua
```

手动单文件 unluac：

```powershell
java -jar unluac.jar path\to\bytecode.lua > path\to\out.lua
```

## 说明

- 复杂/非标准字节码可能触发 unluac 异常；只要仍有 stdout，按「部分成功」保存。  
- 元信息提取失败时自动回退到无 metadata 的格式化。  
- 上游步骤见 [skills/](../../skills/)，可选后处理见 [../postprocess/](../postprocess/)。
