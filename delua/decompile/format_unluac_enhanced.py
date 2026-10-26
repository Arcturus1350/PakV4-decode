#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版格式化脚本，结合 luac-parser-rs 提取的元信息进行更好的格式化
"""

import re
import sys
import os
import json
from pathlib import Path


def load_parser_metadata(bytecode_file, parser_json_file):
    """加载 luac-parser-rs 解析后的元信息"""
    if not os.path.exists(parser_json_file):
        return None
    
    try:
        with open(parser_json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"警告: 无法加载解析元信息: {e}")
        return None


def detect_lua_version(file_path, metadata=None):
    """检测 Lua 版本"""
    if metadata and 'header' in metadata:
        version_hex = metadata['header'].get('lua_version', '51')
        # 将十六进制转换为版本号
        version_map = {
            '51': 'lua51',
            '52': 'lua52',
            '53': 'lua53',
            '54': 'lua54',
        }
        return version_map.get(version_hex, 'lua51')
    return "lua51"


def fix_chinese_encoding(content):
    """尝试修复中文编码问题"""
    def decode_escape(match):
        try:
            nums = []
            for part in match.group(0).split('\\'):
                if part:
                    try:
                        nums.append(int(part))
                    except ValueError:
                        pass
            
            if nums:
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
    
    pattern = r'\\\d{3}(?:\\\d{3})*'
    content = re.sub(pattern, decode_escape, content)
    return content


def optimize_table_initialization(content):
    """优化表格初始化格式 - 将分散的赋值合并为表格初始化"""
    lines = content.split('\n')
    optimized = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检测模式: var = {} 后跟 ;({}).field = value 和 var[idx] = value
        # 例如:
        # L0_0 = {}
        # ;({}).nDamageBase = 0
        # ;({}).nDamageRand = 0
        # local L1_1 = L1_1
        # ;({}).nDamageBase = 844827
        # ...
        # L0_0[1] = L1_1
        
        table_var_match = re.match(r'^(local\s+)?([ALr]\d+_\d+)\s*=\s*\{\}\s*$', stripped)
        if table_var_match:
            is_local = table_var_match.group(1) is not None
            var_name = table_var_match.group(2)
            original_line = line  # 保留原始缩进
            
            i += 1
            table_items = []  # 存储表格项 [(index, value, is_array_item)]
            temp_vars = {}  # 临时变量: var_name -> index
            
            # 第一阶段：收集字段赋值和临时变量定义
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                
                # 匹配 ;({}).field = value 或 {}.field = value（已转换后的格式）
                field_match = re.match(r'^;?\(?\{\}\)?\.(\w+)\s*=\s*(.+)$', next_stripped) or re.match(r'^\{\}\.(\w+)\s*=\s*(.+)$', next_stripped)
                if field_match:
                    field_name = field_match.group(1)
                    field_value = field_match.group(2).rstrip(',')
                    table_items.append(('field', field_name, field_value))
                    i += 1
                    continue
                
                # 匹配 local Lx_y = Lx_y (临时变量定义)
                temp_var_match = re.match(r'^local\s+([ALr]\d+_\d+)\s*=\s*\1\s*$', next_stripped)
                if temp_var_match:
                    temp_var_name = temp_var_match.group(1)
                    # 继续查找这个临时变量的字段赋值
                    temp_fields = []
                    i += 1
                    while i < len(lines):
                        field_line = lines[i].strip()
                        field_match = re.match(r'^;?\(?\{\}\)?\.(\w+)\s*=\s*(.+)$', field_line) or re.match(r'^\{\}\.(\w+)\s*=\s*(.+)$', field_line)
                        if field_match:
                            temp_fields.append((field_match.group(1), field_match.group(2).rstrip(',')))
                            i += 1
                        else:
                            break
                    
                    # 创建临时变量的表格初始化
                    if temp_fields:
                        temp_var_idx = len(table_items) + 1
                        temp_vars[temp_var_name] = temp_var_idx
                        table_items.append(('array', temp_var_idx, temp_fields))
                    continue
                
                # 匹配 var[idx] = value (索引赋值)
                index_match = re.match(rf'^{re.escape(var_name)}\[(\d+)\]\s*=\s*(.+)$', next_stripped)
                if index_match:
                    idx = int(index_match.group(1))
                    val = index_match.group(2).strip()
                    # 检查是否是已收集的临时变量
                    if val in temp_vars:
                        # 已经是表格项的一部分
                        pass
                    else:
                        table_items.append(('index', idx, val))
                    i += 1
                    continue
                
                # 其他情况，停止收集
                break
            
            # 生成优化的表格初始化代码
            if table_items:
                # 计算缩进
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = ' ' * indent
                
                # 生成表格开始
                prefix = 'local ' if is_local else ''
                optimized.append(f"{indent_str}{prefix}{var_name} = {{")
                
                # 添加表格项
                array_items = []  # 数组项（按索引顺序）
                hash_items = []   # 哈希项（字段）
                
                for item_type, key, value in table_items:
                    if item_type == 'field':
                        # 字段赋值
                        hash_items.append((key, value))
                    elif item_type == 'array':
                        # 数组项（子表格）
                        # key 是索引 idx，value 是字段列表 fields
                        idx = key
                        fields = value
                        sub_table = "{\n"
                        for field_name, field_value in fields:
                            sub_table += f"{indent_str}    {field_name} = {field_value},\n"
                        sub_table += f"{indent_str}  }}"
                        array_items.append((idx, sub_table))
                    elif item_type == 'index':
                        # 直接索引赋值
                        # key 是索引，value 是值
                        array_items.append((key, value))
                
                # 先添加数组项（按索引排序）
                for idx, val in sorted(array_items, key=lambda x: x[0]):
                    optimized.append(f"{indent_str}  [{idx}] = {val},")
                
                # 再添加哈希项
                for field_name, field_value in hash_items:
                    optimized.append(f"{indent_str}  {field_name} = {field_value},")
                
                optimized.append(f"{indent_str}}}")
            else:
                # 没有收集到内容，保持原样
                optimized.append(line)
        else:
            optimized.append(line)
            i += 1
    
    return '\n'.join(optimized)


def improve_code_structure(content, metadata=None):
    """改进代码结构"""
    lines = content.split('\n')
    improved = []
    
    # 移除无意义的赋值
    for line in lines:
        stripped = line.strip()
        
        # 移除 local var = var 这种无意义赋值
        if re.match(r'^local\s+r\d+_\d+\s*=\s*r\d+_\d+\s*$', stripped):
            continue
        
        # 注意：不要在这里移除 ;({})，让 optimize_table_initialization 先处理
        # 只移除单独的分号
        if stripped == ';':
            continue
        
        improved.append(stripped)
    
    content = '\n'.join(improved)
    
    # 优化表格初始化（已经在主函数中调用，这里不再调用）
    # content = optimize_table_initialization(content)
    
    return content


def convert_variable_names_improved(content, metadata=None):
    """改进的变量名转换"""
    # 使用与原来相同的逻辑，但可以考虑使用 metadata 中的 locals 信息
    variable_pattern = re.compile(r'\b([AL])(\d+)_(\d+)\b')
    variables = {}
    counter = {}
    
    def replace_var(match):
        prefix = match.group(1)
        first_num = int(match.group(2))
        second_num = int(match.group(3))
        
        key = f"{prefix}_{first_num}_{second_num}"
        
        if key not in variables:
            if prefix == 'A':
                new_name = f"r{first_num}_{second_num}"
            else:
                if first_num not in counter:
                    counter[first_num] = {}
                if second_num not in counter[first_num]:
                    counter[first_num][second_num] = len(counter[first_num])
                var_idx = counter[first_num][second_num]
                new_name = f"r{first_num}_{var_idx}"
            variables[key] = new_name
        return variables[key]
    
    content = variable_pattern.sub(replace_var, content)
    return content


def restore_function_names_improved(content):
    """改进的函数名恢复"""
    lines = content.split('\n')
    function_names = {}
    
    # 匹配 FunctionName = variable 格式
    for line in lines:
        match = re.match(r'^(\w+)\s*=\s*([ALr]\d+_\d+)\s*$', line.strip())
        if match:
            func_name = match.group(1)
            var_name = match.group(2)
            if func_name[0].isupper() or func_name in ['CanCast', 'Apply', 'UnApply', 'OnRemove', 'OnEarlyWarning', 'OnChannelBegin', 'OnChannelEnd', 'GetSkillLevelData', 'OnSkillLevelUp', 'OnSkillForgotten', 'Include']:
                function_names[var_name] = func_name
    
    # 替换函数定义
    for var_name, func_name in function_names.items():
        escaped_var = re.escape(var_name)
        content = re.sub(
            rf'\bfunction\s+{escaped_var}\(',
            f'function {func_name}(',
            content
        )
    
    return content


def add_line_comments(content, metadata=None):
    """添加行号注释（如果有元信息）"""
    if not metadata or 'main_chunk' not in metadata:
        return content
    
    lines = content.split('\n')
    formatted = []
    
    # 提取函数原型信息
    prototypes = []
    main_chunk = metadata.get('main_chunk', {})
    
    # 收集所有函数原型（包括嵌套的）
    def collect_prototypes(proto, parent_offset=0):
        prototypes.append({
            'line_defined': proto.get('line_defined', 0),
            'last_line_defined': proto.get('last_line_defined', 0),
            'num_params': proto.get('num_params', 0),
        })
        for nested in proto.get('prototypes', []):
            collect_prototypes(nested, parent_offset)
    
    collect_prototypes(main_chunk)
    for proto in main_chunk.get('prototypes', []):
        collect_prototypes(proto)
    
    # 函数计数器
    function_id = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检测函数定义
        if re.match(r'^\s*function\s+\w+\(', stripped):
            function_id += 1
            formatted.append(line)
            
            # 尝试找到对应的原型
            proto = None
            if function_id <= len(prototypes):
                proto = prototypes[function_id - 1]
            
            # 添加行号注释
            if proto and proto.get('line_defined', 0) > 0:
                line_start = proto.get('line_defined', 0)
                line_end = proto.get('last_line_defined', line_start)
                formatted.append(f"  -- line: [{line_start}, {line_end}] id: {function_id}")
            else:
                # 如果没有精确信息，添加占位符
                formatted.append(f"  -- line: [0, 0] id: {function_id}")
        else:
            formatted.append(line)
        
        i += 1
    
    return '\n'.join(formatted)


def optimize_temp_variable_usage(content):
    """优化临时变量的使用，将简单计算内联"""
    lines = content.split('\n')
    optimized = []
    i = 0
    
    while i < len(lines):
        if i >= len(lines):
            break
            
        line = lines[i]
        stripped = line.strip()
        
        # 遇到 end 时，临时变量作用域结束，可以清空相关记录
        # （这个功能可以用于更复杂的优化，目前先记录）
        
        # 检测模式: 
        #   var = CONSTANT
        #   var = EXPR * var  或  var = var * EXPR
        #   target = var
        # 
        # 应该优化为:
        #   target = EXPR * CONSTANT
        
        # 匹配: var = CONSTANT (常量名通常是大写字母开头，可能包含下划线)
        match_const = re.match(r'^([rAL]\d+_\d+)\s*=\s*([A-Z_][A-Z0-9_]*)$', stripped)
        if match_const:
            temp_var = match_const.group(1)
            constant = match_const.group(2)
            
            # 检查下一行是否是计算
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # 匹配: var = EXPR * var
                match_calc1 = re.match(rf'^{re.escape(temp_var)}\s*=\s*(.+?)\s*\*\s*{re.escape(temp_var)}\s*$', next_line)
                # 匹配: var = var * EXPR
                match_calc2 = re.match(rf'^{re.escape(temp_var)}\s*=\s*{re.escape(temp_var)}\s*\*\s*(.+?)\s*$', next_line)
                
                match_calc = match_calc1 or match_calc2
                if match_calc:
                    # 获取表达式部分
                    expr = match_calc1.group(1) if match_calc1 else match_calc2.group(1)
                    
                    # 检查下下行是否是最终赋值
                    if i + 2 < len(lines):
                        final_line = lines[i + 2].strip()
                        # 匹配: target = var
                        match_final = re.match(rf'^(.+?)\s*=\s*{re.escape(temp_var)}\s*$', final_line)
                        
                        if match_final:
                            target = match_final.group(1)
                            
                            # 检查后续代码中变量的使用情况
                            can_optimize = False
                            
                            # 查找下一个重新赋值或者 end 语句
                            found_reassign = False
                            found_end = False
                            found_other_use = False
                            
                            for j in range(i + 3, len(lines)):
                                check_line = lines[j].strip()
                                
                                # 检查是否是 end（函数结束，临时变量作用域结束）
                                if check_line == 'end':
                                    found_end = True
                                    can_optimize = True  # 到函数结束都没其他使用，可以优化
                                    break
                                
                                # 检查是否重新赋值
                                if re.match(rf'^{re.escape(temp_var)}\s*=\s*', check_line):
                                    found_reassign = True
                                    can_optimize = True  # 重新赋值，说明这三行是独立的，可以优化
                                    break
                                
                                # 检查是否有其他使用（但不在赋值语句的左侧）
                                # 只检查不在赋值左侧的使用
                                if re.search(rf'\b{re.escape(temp_var)}\b', check_line):
                                    # 检查是否在赋值左侧
                                    match_assign = re.match(rf'^(.+?)\s*=\s*', check_line)
                                    if not match_assign or temp_var not in match_assign.group(1):
                                        # 在表达式中使用，需要保留
                                        found_other_use = True
                                        break
                            
                            # 如果没找到重新赋值、end 或其他使用，检查是否在函数末尾
                            if not found_reassign and not found_end and not found_other_use:
                                # 检查后续10行内是否有 end
                                for j in range(i + 3, min(i + 15, len(lines))):
                                    if lines[j].strip() == 'end':
                                        can_optimize = True
                                        break
                                # 如果已经是文件末尾附近，也可以优化
                                if i + 3 >= len(lines) - 5:
                                    can_optimize = True
                            
                            if can_optimize:
                                # 优化为: target = expr * constant
                                # 保留原始缩进
                                indent = len(line) - len(line.lstrip())
                                indent_str = ' ' * indent
                                optimized.append(f"{indent_str}{target} = {expr} * {constant}")
                                i += 3  # 跳过这三行
                                continue
        
        optimized.append(line)
        i += 1
    
    return '\n'.join(optimized)


def clean_code_format_improved(content):
    """改进的代码清理"""
    lines = content.split('\n')
    cleaned = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 移除多余的空行（连续两个以上只保留一个）
        if not stripped:
            if cleaned and cleaned[-1].strip():
                cleaned.append('')
            continue
        
        cleaned.append(stripped)
    
    # 统一缩进（2个空格）
    formatted = []
    indent_level = 0
    
    for line in cleaned:
        if not line:
            formatted.append('')
            continue
        
        # 减少缩进
        if line.startswith('end') or line.startswith('else'):
            indent_level = max(0, indent_level - 1)
        
        # 添加缩进
        indented = ' ' * (indent_level * 2) + line
        formatted.append(indented)
        
        # 增加缩进
        if line.endswith('then') or line.endswith('do') or (line.startswith('function') and not line.endswith('end')):
            indent_level += 1
        elif line.startswith('if') and not line.endswith('then'):
            indent_level += 1
    
    return '\n'.join(formatted)


def add_header_comments(content, filename="", metadata=None):
    """添加文件头注释"""
    version = detect_lua_version(None, metadata)
    header = f"""-- filename: {filename}
-- version: {version}
-- line: [0, 0] id: 0
"""
    return header + content


def format_unluac_enhanced(input_file, output_file=None, parser_json_file=None):
    """增强版格式化函数"""
    
    with open(input_file, 'rb') as f:
        content = f.read()
    
    # 尝试解码
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
    
    # 加载元信息（如果有）
    metadata = None
    if parser_json_file:
        metadata = load_parser_metadata(input_file, parser_json_file)
    
    # 执行转换步骤
    text = fix_chinese_encoding(text)
    text = restore_function_names_improved(text)
    text = convert_variable_names_improved(text, metadata)
    text = restore_function_names_improved(text)  # 再次恢复（变量名转换后）
    # 先优化表格初始化（需要在变量名转换后）
    # 注意：此时可能已经是 {}.field 格式了，需要同时匹配两种格式
    text = optimize_table_initialization(text)
    text = improve_code_structure(text, metadata)  # 清理无意义赋值
    # 清理剩余的格式（如果优化表格时没有匹配到的）
    # 先处理带分号的，再处理不带分号的
    text = text.replace(';({})', '{}').replace(';({', '{')
    text = text.replace('({})', '{}').replace('({', '{')
    # 处理 {}.field = value 这种格式（可能需要更复杂的处理）
    text = optimize_temp_variable_usage(text)  # 优化临时变量使用
    text = clean_code_format_improved(text)
    text = add_line_comments(text, metadata)  # 添加行号注释
    text = add_header_comments(text, os.path.basename(input_file), metadata)
    
    # 输出文件
    if output_file is None:
        output_file = input_file.replace('.lua', '_enhanced.lua')
    
    with open(output_file, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(text)
    
    print(f"格式化完成: {input_file} -> {output_file}")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python format_unluac_enhanced.py <输入文件> [输出文件] [解析JSON文件]")
        print("示例: python format_unluac_enhanced.py output.lua output_enhanced.lua parser_info.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    parser_json = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 {input_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        success = format_unluac_enhanced(input_file, output_file, parser_json)
        if not success:
            print(f"错误: 格式化失败", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"错误: 格式化过程中出现异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

