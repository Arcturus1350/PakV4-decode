#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量使用 unluac 解码 Lua 字节码文件，并转换为 metaworm 格式
"""

import os
import sys
import subprocess
from pathlib import Path


def find_unluac_jar():
    """查找 unluac.jar 文件"""
    current_dir = Path(__file__).parent
    jar_path = current_dir / "unluac.jar"
    
    if jar_path.exists():
        return str(jar_path)
    
    # 尝试在当前目录查找
    if os.path.exists("unluac.jar"):
        return "unluac.jar"
    
    print("错误: 找不到 unluac.jar 文件")
    print("请将 unluac.jar 放在当前目录或脚本所在目录")
    return None


def decompile_file(jar_path, input_file, output_file=None, error_log=None):
    """解码单个文件"""
    if output_file is None:
        output_file = input_file  # 覆盖原文件
    
    try:
        # 运行 unluac
        result = subprocess.run(
            ["java", "-jar", jar_path, input_file],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30  # 设置超时，避免卡死
        )
        
        # 检查是否有真正的错误（不是警告）
        stderr_text = result.stderr or ""
        has_exception = "Exception" in stderr_text
        has_warning = "Warning" in stderr_text
        has_output = bool(result.stdout.strip())
        
        # 关键逻辑：只要有输出，即使有 Exception 也算部分成功
        # 只有在完全没有输出时才视为真正的错误
        if not has_output:
            # 输出为空，视为错误
            error_msg = "输出为空"
            if stderr_text:
                error_msg += f" ({stderr_text.split(chr(10))[0]})"
            print(f"  ❌ 解码失败: {error_msg}")
            if error_log is not None:
                error_log.append((input_file, error_msg))
            return False
        elif has_exception and has_output:
            # 有 Exception 但有输出，部分成功
            exception_type = ""
            for line in stderr_text.split('\n'):
                if 'Exception' in line:
                    exception_type = line.split(':')[0] if ':' in line else "Exception"
                    break
            
            print(f"  ⚠️  部分成功（有 {exception_type} 但已输出内容）")
            # 继续处理，保存输出
        elif has_warning and has_output:
            # 只有警告，显示但不阻止处理
            warning_msg = stderr_text.split('\n')[0] if stderr_text else ""
            if warning_msg and "Warning" in warning_msg:
                print(f"  ⚠️  {warning_msg}")
        
        # 写入输出文件
        try:
            with open(output_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(result.stdout)
        except Exception as e:
            print(f"  ❌ 写入文件失败: {e}")
            return False
        
        # 尝试提取元信息（如果 luac-parser-rs 可用）
        metadata_file = None
        # 优先使用工作区根目录下的 luac-parser-rs，其次兼容同级目录
        luac_parser_dir = Path(__file__).parent.parent / "luac-parser-rs"
        if not luac_parser_dir.exists():
            luac_parser_dir = Path(__file__).parent / "luac-parser-rs"
        if luac_parser_dir.exists():
            # 尝试使用 Rust 工具提取元信息
            bytecode_file = input_file  # 原始字节码文件
            metadata_path = Path(output_file).with_suffix('.metadata.json')
            
            try:
                rust_result = subprocess.run([
                    "cargo", "run", "--example", "export_metadata", "--",
                    str(bytecode_file)
                ], 
                cwd=str(luac_parser_dir),
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
                )
                
                if rust_result.returncode == 0 and rust_result.stdout.strip():
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        f.write(rust_result.stdout)
                    metadata_file = str(metadata_path)
                elif rust_result.stderr:
                    # 如果有错误但不影响后续处理，可以忽略
                    pass
            except Exception as e:
                # Rust 工具不可用或出错，忽略（继续使用无元信息的格式化）
                pass
        
        # 格式化输出
        if output_file.endswith('.lua'):
            # 优先使用增强版格式化脚本
            format_script = Path(__file__).parent / "format_unluac_enhanced.py"
            if not format_script.exists():
                format_script = Path(__file__).parent / "format_unluac_output.py"
            
            if format_script.exists():
                cmd = [
                    sys.executable,
                    str(format_script),
                    str(output_file),
                    str(output_file)  # 覆盖已解码的文件
                ]
                
                # 如果有元信息文件，添加到命令
                if metadata_file:
                    cmd.append(metadata_file)
                
                format_result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                if format_result.returncode != 0:
                    print(f"  ⚠️  格式化失败，但解码成功")
                    if format_result.stderr:
                        error_msg = format_result.stderr[:200]  # 只显示前200字符
                        print(f"      错误信息: {error_msg}")
                    elif format_result.stdout:
                        output_msg = format_result.stdout[:200]
                        print(f"      输出信息: {output_msg}")
                elif metadata_file:
                    # 格式化成功，删除临时元信息文件（可选，如果想保留可以注释掉）
                    try:
                        os.remove(metadata_file)
                    except:
                        pass
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"  ❌ 超时（超过30秒）")
        if error_log is not None:
            error_log.append((input_file, "处理超时"))
        return False
    except Exception as e:
        print(f"  ❌ 异常: {str(e)[:100]}")
        if error_log is not None:
            error_log.append((input_file, str(e)))
        return False


def batch_decompile(source_dir, output_dir=None, file_pattern="*.lua"):
    """批量解码文件"""
    jar_path = find_unluac_jar()
    if not jar_path:
        return False
    
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"错误: 源目录不存在: {source_dir}")
        return False
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = source_path
    
    # 查找所有 .lua 文件
    lua_files = list(source_path.rglob(file_pattern))
    
    if not lua_files:
        print(f"未找到任何 {file_pattern} 文件")
        return False
    
    print(f"找到 {len(lua_files)} 个文件，开始解码...\n")
    
    success_count = 0
    failed_count = 0
    error_log = []  # 记录失败的文件和错误信息
    
    for i, lua_file in enumerate(lua_files, 1):
        # 计算输出路径
        if output_dir:
            relative_path = lua_file.relative_to(source_path)
            output_file = output_path / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_file = lua_file
        
        print(f"[{i}/{len(lua_files)}] {lua_file.name}", end=" ... ")
        
        if decompile_file(jar_path, str(lua_file), str(output_file), error_log):
            success_count += 1
            print("✓ 成功")
        else:
            failed_count += 1
    
    # 输出统计信息
    print(f"\n" + "="*60)
    print(f"处理完成!")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {failed_count} 个文件")
    
    # 保存失败文件列表
    if error_log:
        error_log_file = output_path / "decompile_errors.txt"
        with open(error_log_file, 'w', encoding='utf-8') as f:
            f.write("解码失败的文件列表:\n")
            f.write("="*60 + "\n\n")
            for file_path, error in error_log:
                f.write(f"文件: {file_path}\n")
                f.write(f"错误: {error[:200]}\n")  # 只保存前200个字符
                f.write("-"*60 + "\n")
        print(f"\n失败文件列表已保存到: {error_log_file}")
        print(f"\n失败的文件:")
        for file_path, _ in error_log:
            print(f"  - {file_path}")
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python batch_decompile.py <源目录> [输出目录]")
        print("示例: python batch_decompile.py new dec")
        print("       python batch_decompile.py new  # 覆盖原文件")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    batch_decompile(source_dir, output_dir)

