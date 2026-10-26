# delua — 后处理工具集

承接主流程 **第 3 步**：对技能提取得到的加密 `.lua`（字节码）做反编译与格式化；并附带若干旁路工具。

本目录只保留脚本与依赖源码，不长期存放输入/输出数据。

## 目录

| 目录 | 主流程角色 | 说明 |
|------|------------|------|
| [decompile/](decompile/) | ★ 必需 | unluac 批量反编译 + 格式化 |
| [luac-parser-rs/](luac-parser-rs/) | 可选 | Rust 解析器，给增强格式化提供元信息 |
| [postprocess/](postprocess/) | 可选 | 按首领分目录、补 Default.lua 注释 |
| [jx3dat/](jx3dat/) | 旁路 | `.jx3dat` 生成、裁剪、比对 |
| [utils/](utils/) | 旁路 | 通用小工具（如文件名处理） |

---

## 最常用：批量反编译

1. 在**仓库根目录**准备临时目录，例如 `input/`、`output/`  
2. 把第 2 步得到的字节码 `.lua` 放进 `input/`  
3. 执行：

```powershell
cd delua\decompile
python batch_decompile.py ..\..\input ..\..\output
```

4. 结果在 `output/`；失败列表见 `output\decompile_errors.txt`

更完整说明：[decompile/README.md](decompile/README.md)

可选后处理（洛阳之战一类按首领分目录）：见 [postprocess/README.md](postprocess/README.md)。

---

## 约定

- 各子目录用法见对应 `README.md`。  
- `input/` / `output/` / `*_技能脚本*` 等用完可删，勿堆进工具目录。  
- `luac-parser-rs` 需要时再 `cargo build`；`target/` 可随时删除。
