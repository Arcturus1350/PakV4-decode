#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 unluac 的输出格式转换为 metaworm's luadec 的格式
"""

import re
import sys
import os
from pathlib import Path


def detect_lua_version(file_path):
    """检测 Lua 版本，默认为 lua51"""
    # 可以读取文件头来判断，这里暂时返回默认值
    return "lua51"


def convert_variable_names(content):
    """将 unluac 的变量名格式转换为 r0_1 格式"""
    
    # 定义变量名映射规则
    # L0_0, L1_5, A0_4, A1_12 等格式转换为 r0_1, r1_1 格式
    
    # 先找出所有需要替换的变量名
    variable_pattern = re.compile(r'\b([AL])(\d+)_(\d+)\b')
    
    # 收集所有变量名并建立映射
    variables = {}
    counter = {}
    
    def replace_var(match):
        prefix = match.group(1)  # L 或 A
        first_num = int(match.group(2))
        second_num = int(match.group(3))
        
        # 创建唯一标识符
        key = f"{prefix}_{first_num}_{second_num}"
        
        if key not in variables:
            # 如果是 A（函数参数），保持第一个数字为 0
            if prefix == 'A':
                new_name = f"r{first_num}_{second_num}"
            else:
                # L 开头的局部变量，转换为 r 格式
                # 根据出现的顺序分配编号
                if first_num not in counter:
                    counter[first_num] = {}
                if second_num not in counter[first_num]:
                    counter[first_num][second_num] = len(counter[first_num])
                var_idx = counter[first_num][second_num]
                new_name = f"r{first_num}_{var_idx}"
            variables[key] = new_name
        return variables[key]
    
    # 替换变量名
    content = variable_pattern.sub(replace_var, content)
    
    return content


def fix_chinese_encoding(content):
    """尝试修复中文编码问题"""
    # unluac 输出的中文可能是转义序列，如 \187\225\213\189
    # 这些通常是 GBK 或 UTF-8 编码的字节序列
    
    # 尝试匹配 \xxx\xxx 格式的转义序列
    def decode_escape(match):
        try:
            # 提取所有数字
            nums = []
            for part in match.group(0).split('\\'):
                if part:
                    try:
                        nums.append(int(part))
                    except ValueError:
                        pass
            
            if nums:
                # 尝试解码为 GBK（常见中文编码）
                try:
                    bytes_data = bytes(nums)
                    decoded = bytes_data.decode('gbk')
                    return decoded
                except:
                    try:
                        decoded = bytes_data.decode('utf-8')
                        return decoded
                    except:
                        pass
            
            return match.group(0)
        except:
            return match.group(0)
    
    # 匹配 \数字\数字 格式
    pattern = r'\\\d{3}(?:\\\d{3})*'
    content = re.sub(pattern, decode_escape, content)
    
    return content


def restore_function_names(content, before_var_conversion=False):
    """尝试恢复函数名"""
    # 查找类似 GetSkillLevelData = L0_0 或 GetSkillLevelData = r0_0 的赋值
    lines = content.split('\n')
    function_names = {}  # 映射：变量名 -> 真实函数名
    
    # 匹配模式：FunctionName = VariableName
    pattern_after = r'^(\w+)\s*=\s*(r\d+_\d+)\s*$'  # 变量名已转换后
    pattern_before = r'^(\w+)\s*=\s*([AL]\d+_\d+)\s*$'  # 变量名未转换前
    
    pattern = pattern_before if before_var_conversion else pattern_after
    
    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            func_name = match.group(1)
            var_name = match.group(2)
            # 只保留看起来像函数名的（首字母大写，或常见的函数名）
            if func_name[0].isupper() or func_name in ['CanCast', 'Apply', 'UnApply', 'OnRemove', 'OnEarlyWarning', 'OnChannelBegin', 'OnChannelEnd', 'GetSkillLevelData', 'OnSkillLevelUp', 'OnSkillForgotten', 'Include']:
                function_names[var_name] = func_name
    
    # 替换函数定义中的变量名为真实函数名
    for var_name, func_name in function_names.items():
        # 匹配 "function var_name(" 格式，需要转义特殊字符
        escaped_var = re.escape(var_name)
        content = re.sub(
            rf'\bfunction\s+{escaped_var}\(',
            f'function {func_name}(',
            content
        )
    
    return content


def clean_code_format(content):
    """清理代码格式"""
    lines = content.split('\n')
    cleaned = []
    in_table = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 移除多余的分号
        stripped = stripped.replace(';({})', '{}')
        stripped = stripped.replace(';({', '{')
        
        # 移除单独的分号行
        if stripped == ';':
            continue
        
        # 移除无意义的赋值：local var = var 或 var = var
        if re.match(r'^(local\s+)?r\d+_\d+\s*=\s*r\d+_\d+\s*$', stripped):
            continue
        
        # 处理 {}.field = value 格式，转换为表格初始化
        # 这个比较复杂，暂时保留原样
        
        # 移除多余的空行（连续两个以上空行只保留一个）
        if not stripped:
            if cleaned and cleaned[-1].strip():
                cleaned.append('')
            continue
        
        cleaned.append(stripped)
    
    return '\n'.join(cleaned)


def add_header_comments(content, filename=""):
    """添加文件头注释"""
    version = detect_lua_version(None)
    header = f"""-- filename: {filename}
-- version: {version}
-- line: [0, 0] id: 0
"""
    return header + content


def format_function_lines(content):
    """为函数添加行号注释（如果需要的话）"""
    # 这个功能需要从原始字节码中提取行号信息
    # 如果没有原始信息，可以跳过或使用占位符
    # 暂时不实现，因为需要字节码解析
    
    # 可以在函数定义后添加注释占位符
    lines = content.split('\n')
    formatted = []
    
    for i, line in enumerate(lines):
        # 检测函数定义
        if re.match(r'^\s*function\s+\w+\(', line):
            # 下一行添加注释占位符
            formatted.append(line)
            # 添加行号注释（使用占位符）
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith('--'):
                # 估算行号（不准确，但可以作为占位符）
                formatted.append(f"  -- line: [{i + 1}, {i + 10}] id: 1")
        else:
            formatted.append(line)
    
    return '\n'.join(formatted)


def reformat_code(content):
    """重新格式化代码，使其更易读"""
    lines = content.split('\n')
    formatted = []
    indent_level = 0
    indent_size = 2
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted.append('')
            continue
        
        # 计算缩进
        if stripped.startswith('end') or stripped.startswith('else') or stripped.startswith('elseif'):
            indent_level = max(0, indent_level - 1)
        
        # 添加缩进
        indented = ' ' * (indent_level * indent_size) + stripped
        formatted.append(indented)
        
        # 调整缩进级别
        if stripped.endswith('then') or stripped.endswith('do') or stripped.endswith('{'):
            indent_level += 1
        elif stripped.startswith('function'):
            indent_level += 1
    
    return '\n'.join(formatted)


def convert_unluac_to_metaworm_format(input_file, output_file=None):
    """将 unluac 输出转换为 metaworm 格式"""
    
    with open(input_file, 'rb') as f:
        content = f.read()
    
    # 尝试不同的编码
    text = None
    for encoding in ['utf-8', 'gbk', 'latin1']:
        try:
            text = content.decode(encoding)
            break
        except:
            continue
    
    if text is None:
        print(f"错误: 无法解码文件 {input_file}")
        return False
    
    # 执行转换步骤
    text = fix_chinese_encoding(text)
    # 先尝试恢复函数名（在变量名转换之前，因为需要匹配原始格式）
    text = restore_function_names(text, before_var_conversion=True)
    text = convert_variable_names(text)
    # 再次尝试恢复函数名（在变量名转换之后）
    text = restore_function_names(text, before_var_conversion=False)
    text = clean_code_format(text)
    text = add_header_comments(text, os.path.basename(input_file))
    # text = format_function_lines(text)  # 暂时不添加，因为需要原始字节码信息
    # text = reformat_code(text)  # 暂时不重新格式化，保持原有结构
    
    # 输出文件
    if output_file is None:
        output_file = input_file.replace('.lua', '_formatted.lua')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"转换完成: {input_file} -> {output_file}")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python format_unluac_output.py <输入文件> [输出文件]")
        print("示例: python format_unluac_output.py output.lua output_formatted.lua")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 {input_file}")
        sys.exit(1)
    
    convert_unluac_to_metaworm_format(input_file, output_file)

