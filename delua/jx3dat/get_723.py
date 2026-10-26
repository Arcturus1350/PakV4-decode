#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理jx3dat文件，保留所有二级结构，并在每个二级结构内只保留[723] = {三级结构及其内容
"""

def find_block_end(lines, start_idx):
    """
    找到从start_idx开始的大括号块的结束位置
    
    Args:
        lines: 所有行的列表
        start_idx: 开始行的索引（包含开大括号的行）
    
    Returns:
        int: 结束行的索引（包含闭大括号的行），如果找不到则返回-1
    """
    brace_count = 0
    for i in range(start_idx, len(lines)):
        line = lines[i]
        # 统计大括号
        brace_count += line.count('{') - line.count('}')
        if brace_count == 0:
            return i
    return -1

def extract_723_block(lines, start_idx, end_idx):
    """
    在指定范围内提取[723] = {块及其所有内容
    
    Args:
        lines: 所有行的列表
        start_idx: 范围的开始索引
        end_idx: 范围的结束索引
    
    Returns:
        list: [723] = {块的所有行，如果不存在则返回空列表
    """
    result = []
    i = start_idx
    while i <= end_idx:
        line = lines[i]
        # 检查是否是[723] = {开头（二级tab缩进）
        if line.startswith('\t\t') and '[723] = {' in line:
            # 找到这个块的结束位置
            block_end = find_block_end(lines, i)
            if block_end != -1:
                # 提取整个块
                result.extend(lines[i:block_end+1])
                i = block_end + 1
                continue
        i += 1
    return result

def process_jx3dat_file(input_file, output_file):
    """
    处理jx3dat文件，保留所有二级结构，并在每个二级结构内只保留[723] = {三级结构及其内容
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找所有顶级二级结构（只有一级缩进的键）
        top_level_keys = []
        for i, line in enumerate(lines):
            # 检查是否是顶级键（以tab开头，包含 = {，但不是二级tab）
            if line.startswith('\t') and ' = {' in line and not line.startswith('\t\t'):
                key_name = line.strip().split(' = {')[0]
                top_level_keys.append((i, key_name, line))
        
        if not top_level_keys:
            print("错误：未找到任何顶级二级结构")
            return False
        
        print(f"找到 {len(top_level_keys)} 个顶级二级结构：")
        for i, (line_num, key_name, line) in enumerate(top_level_keys):
            print(f"  {i+1}. {key_name} (第{line_num+1}行)")
        
        # 构建结果内容
        result_lines = []
        result_lines.append("return {\n")
        
        # 处理每个二级结构
        for i, (line_num, key_name, line) in enumerate(top_level_keys):
            # 确定下一个二级结构的开始位置，以确定当前二级结构的范围
            if i + 1 < len(top_level_keys):
                next_line_num = top_level_keys[i + 1][0]
            else:
                # 最后一个二级结构，找到文件末尾或return块的结束
                next_line_num = len(lines)
            
            # 找到当前二级结构块的结束位置
            block_start = line_num
            block_end = find_block_end(lines, block_start)
            
            if block_end == -1:
                print(f"警告：无法找到 {key_name} 块的结束位置，跳过")
                continue
            
            # 限制在下一个二级结构之前
            if block_end >= next_line_num:
                block_end = next_line_num - 1
            
            # 提取[723] = {块
            key_723_block = extract_723_block(lines, block_start + 1, block_end - 1)
            
            # 添加二级结构的开始行
            result_lines.append(line.rstrip() + "\n")
            
            # 如果有[723] = {块，添加它
            if key_723_block:
                result_lines.extend(key_723_block)
                print(f"  在 {key_name} 中找到 [723] = {{ 块")
            else:
                print(f"  在 {key_name} 中未找到 [723] = {{ 块")
            
            # 添加二级结构的闭合
            result_lines.append("\t},\n")
        
        # 添加最终的闭合大括号
        result_lines.append("}")
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(result_lines)
        
        print(f"\n处理完成！")
        print(f"输入文件：{input_file}")
        print(f"输出文件：{output_file}")
        print(f"原文件行数：{len(lines)}")
        print(f"处理后行数：{len(result_lines)}")
        
        return True
        
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
        return False
    except Exception as e:
        print(f"处理文件时发生错误：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    input_file = "ngb_new.jx3dat"
    output_file = "new1.jx3dat"
    
    print("开始处理jx3dat文件...")
    success = process_jx3dat_file(input_file, output_file)
    
    if success:
        print("文件处理成功！")
        
        # 显示处理后的文件内容
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                result = f.read()
            print("\n处理后的文件内容：")
            print("-" * 50)
            print(result)
            print("-" * 50)
        except Exception as e:
            print(f"读取输出文件时出错：{e}")
    else:
        print("文件处理失败！")

if __name__ == "__main__":
    main()
