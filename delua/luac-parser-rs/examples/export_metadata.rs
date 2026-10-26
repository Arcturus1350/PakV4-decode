//! 导出 Lua 字节码的元信息为 JSON 格式
//! 
//! 使用方法:
//! cargo run --example export_metadata -- 1.lua > metadata.json

use std::env;
use std::fs;
use std::io;
use luac_parser::parse;
use serde_json::json;

fn serialize_metadata(bytecode: &luac_parser::LuaBytecode) -> serde_json::Value {
    let metadata = json!({
        "header": {
            "lua_version": format!("{:02x}", bytecode.header.lua_version),
            "format_version": bytecode.header.format_version,
            "big_endian": bytecode.header.big_endian,
            "int_size": bytecode.header.int_size,
            "size_t_size": bytecode.header.size_t_size,
        },
        "main_chunk": serialize_chunk(&bytecode.main_chunk, 0)
    });
    
    metadata
}

fn serialize_chunk(chunk: &luac_parser::LuaChunk, depth: usize) -> serde_json::Value {
    let mut chunk_json = serde_json::json!({
        "name": String::from_utf8_lossy(&chunk.name),
        "line_defined": chunk.line_defined,
        "last_line_defined": chunk.last_line_defined,
        "num_params": chunk.num_params,
        "num_upvalues": chunk.num_upvalues,
        "locals": chunk.locals.iter().map(|local| {
            json!({
                "name": local.name,
                "start_pc": local.start_pc,
                "end_pc": local.end_pc,
            })
        }).collect::<Vec<_>>(),
        "source_lines": chunk.source_lines.iter().map(|(pc, line)| {
            json!({
                "pc": pc,
                "line": line,
            })
        }).collect::<Vec<_>>(),
        "constants_count": chunk.constants.len(),
        "prototypes_count": chunk.prototypes.len(),
    });
    
    // 递归处理嵌套的函数
    if !chunk.prototypes.is_empty() {
        chunk_json["prototypes"] = serde_json::Value::Array(
            chunk.prototypes.iter()
                .map(|proto| serialize_chunk(proto, depth + 1))
                .collect()
        );
    }
    
    chunk_json
}

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        eprintln!("用法: cargo run --example export_metadata -- <字节码文件>");
        eprintln!("示例: cargo run --example export_metadata -- 1.lua > metadata.json");
        std::process::exit(1);
    }
    
    let file_path = &args[1];
    
    // 读取文件
    let file_data = match fs::read(file_path) {
        Ok(data) => data,
        Err(e) => {
            eprintln!("错误: 无法读取文件 {}: {}", file_path, e);
            std::process::exit(1);
        }
    };
    
    // 解析字节码
    let bytecode = match parse(&file_data) {
        Ok(bc) => bc,
        Err(e) => {
            eprintln!("错误: 无法解析字节码: {}", e);
            std::process::exit(1);
        }
    };
    
    // 序列化为 JSON
    let metadata = serialize_metadata(&bytecode);
    
    // 输出 JSON
    match serde_json::to_writer_pretty(io::stdout(), &metadata) {
        Ok(_) => {},
        Err(e) => {
            eprintln!("错误: 无法序列化 JSON: {}", e);
            std::process::exit(1);
        }
    }
}

