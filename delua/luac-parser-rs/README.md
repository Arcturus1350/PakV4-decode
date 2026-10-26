[![crates.io](https://img.shields.io/crates/v/luac-parser.svg)](https://crates.io/crates/luac-parser)
[![docs.rs](https://docs.rs/luac-parser/badge.svg)](https://docs.rs/luac-parser)

## 在本工作区中的用途

本目录是 [metaworm/luac-parser-rs](https://github.com/metaworm/luac-parser-rs) 源码，供上层 `decompile/batch_decompile.py` 调用 `examples/export_metadata` 提取字节码元信息，再交给增强格式化脚本使用。

```bash
# 在本目录编译/运行元信息导出示例
cargo run --example export_metadata -- <bytecode.lua>
```

说明：`target/` 为本地编译产物，工作区默认不保留；需要时再 `cargo build` 即可。

---

# luac-parser (中文)

lua字节码解析器, 目前支持 lua51, lua52, lua53, lua54, luajit, luau

这是目前效果最好的lua反编译器 [metaworm's luadec](http://luadec.metaworm.site) 的一部分

可以基于此代码定制你所需的lua字节码解析器，编译成WASM，让[metaworm's luadec][luadec]加载使用，来反编译非官方的lua字节码

得益于[nom][nom]库的灵活性，编写定制的解析器是很简单的一件事情，可以看[这篇文章][write-parser]了解如何编写

# luac-parser (in English)

lua bytecode parser, currently support lua51, lua52, lua53, lua54, luajit, luau

This is part of [metaworm's luadec][luadec], which is the best lua decompiler at present

You can write your custom luac parser based on this code, which can be able to compiling to WASM and loaded by [metaworm's luadec][luadec], to decompile the unofficial lua bytecode

[luadec]: http://luadec.metaworm.site
[nom]: https://github.com/rust-bakery/nom

Thanks to the flexibility of [nom][nom], it is very easy to write your own parser in rust, read [this article][write-parser] to learn how to write a luac parser

[luadec]: http://luadec.metaworm.site
[nom]: https://github.com/rust-bakery/nom
[write-parser]: https://github.com/metaworm/luac-parser-rs/wiki/Write-custom-luac-parser