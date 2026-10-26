#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
处理 new.jx3dat 文件中的 nTime 字段
对于包含 ';' 的 nTime 值，只保留到第一个 ';' 之前的内容（不包含 ';'）
"""

import re

def process_ntime_field(input_file, output_file):
    """
    处理文件中的 nTime 字段
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 nTime = "..." 的模式
    # 使用非贪婪匹配来匹配引号内的内容
    pattern = r'(nTime\s*=\s*")([^"]*)"'
    
    def replace_ntime(match):
        prefix = match.group(1)  # nTime = "
        value = match.group(2)   # 引号内的内容
        
        # 如果包含 ';'，只保留到第一个 ';' 之前
        if ';' in value:
            value = value.split(';')[0]
        
        return prefix + value + '"'
    
    # 替换所有匹配的内容
    processed_content = re.sub(pattern, replace_ntime, content)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"处理完成！")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")

if __name__ == '__main__':
    input_file = 'new.jx3dat'
    output_file = 'new.jx3dat'
    
    # 处理文件（直接覆盖原文件）
    process_ntime_field(input_file, output_file)

