#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较 new 和 old 文件夹中对应子文件夹里同名文件的二进制内容
"""

import os
from pathlib import Path
from collections import defaultdict


def get_subfolder_mapping():
    """
    获取 new 和 old 文件夹的子文件夹对应关系
    new: 1号_巴图仁钦 -> old: 1
    new: 2号_竭勒 -> old: 2
    new: 3号_图南子 -> old: 3
    new: 4号_叶葵 -> old: 4
    new: 5号_尹雪尘 -> old: 5
    new: 周边 -> 无对应（跳过）
    """
    mapping = {}
    for i in range(1, 6):
        new_name = f"{i}号_" + ["", "巴图仁钦", "竭勒", "图南子", "叶葵", "尹雪尘"][i]
        mapping[new_name] = str(i)
    return mapping


def compare_binary_files(file1_path, file2_path):
    """
    比较两个文件的二进制内容是否完全相同
    返回: (是否相同, 文件1大小, 文件2大小)
    """
    try:
        # 直接读取二进制内容进行比较
        with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        size1 = len(content1)
        size2 = len(content2)
        is_same = content1 == content2
        
        return is_same, size1, size2
    except FileNotFoundError as e:
        return None, 0, 0  # 文件不存在
    except Exception as e:
        print(f"    错误: 无法比较文件 - {e}")
        return None, 0, 0


def compare_folders(new_dir, old_dir):
    """
    比较 new 和 old 文件夹中所有对应子文件夹的文件
    """
    new_path = Path(new_dir)
    old_path = Path(old_dir)
    
    if not new_path.exists():
        print(f"错误: new 文件夹不存在: {new_dir}")
        return
    
    if not old_path.exists():
        print(f"错误: old 文件夹不存在: {old_dir}")
        return
    
    # 获取子文件夹映射关系
    subfolder_mapping = get_subfolder_mapping()
    
    # 统计信息
    total_files = 0
    same_files = 0
    different_files = 0
    missing_in_old = 0
    missing_in_new = 0
    errors = 0
    
    # 存储不同文件的详细信息
    differences = []
    
    print("="*80)
    print("开始比较文件...")
    print("="*80)
    print()
    
    # 遍历 new 文件夹下的所有子文件夹
    for new_subfolder_name in sorted(new_path.iterdir()):
        if not new_subfolder_name.is_dir():
            continue
        
        # 跳过周边文件夹（在old中没有对应）
        if new_subfolder_name.name == "周边":
            print(f"跳过: {new_subfolder_name.name} (old中无对应文件夹)")
            continue
        
        # 查找对应的 old 子文件夹
        old_subfolder_name = subfolder_mapping.get(new_subfolder_name.name)
        if not old_subfolder_name:
            print(f"警告: {new_subfolder_name.name} 在映射表中找不到对应关系，跳过")
            continue
        
        new_subfolder = new_subfolder_name
        old_subfolder = old_path / old_subfolder_name
        
        if not old_subfolder.exists():
            print(f"警告: old 中不存在对应文件夹: {old_subfolder_name}，跳过")
            continue
        
        print(f"\n比较子文件夹: {new_subfolder_name.name} <-> {old_subfolder_name}")
        print("-" * 80)
        
        # 获取两个文件夹中的所有文件（只比较文件，不包括子文件夹）
        new_files = {f.name: f for f in new_subfolder.iterdir() if f.is_file()}
        old_files = {f.name: f for f in old_subfolder.iterdir() if f.is_file()}
        
        # 获取所有需要比较的文件名（在new和old中都存在的文件）
        common_files = set(new_files.keys()) & set(old_files.keys())
        only_in_new = set(new_files.keys()) - set(old_files.keys())
        only_in_old = set(old_files.keys()) - set(new_files.keys())
        
        # 比较共同文件
        for filename in sorted(common_files):
            total_files += 1
            new_file_path = new_files[filename]
            old_file_path = old_files[filename]
            
            is_same, size1, size2 = compare_binary_files(new_file_path, old_file_path)
            
            if is_same is None:
                errors += 1
                print(f"  [错误] {filename}")
            elif is_same:
                same_files += 1
                print(f"  [相同] {filename} (大小: {size1} 字节)")
            else:
                different_files += 1
                differences.append({
                    'subfolder': new_subfolder_name.name,
                    'filename': filename,
                    'new_path': str(new_file_path),
                    'old_path': str(old_file_path),
                    'new_size': size1,
                    'old_size': size2
                })
                print(f"  [不同] {filename} (new: {size1} 字节, old: {size2} 字节)")
        
        # 显示只在new中存在的文件
        if only_in_new:
            missing_in_old += len(only_in_new)
            print(f"\n  只在 new 中存在的文件 ({len(only_in_new)} 个):")
            for filename in sorted(only_in_new):
                print(f"    - {filename}")
        
        # 显示只在old中存在的文件
        if only_in_old:
            missing_in_new += len(only_in_old)
            print(f"\n  只在 old 中存在的文件 ({len(only_in_old)} 个):")
            for filename in sorted(only_in_old):
                print(f"    - {filename}")
    
    # 输出统计信息
    print("\n" + "="*80)
    print("比较完成！统计信息:")
    print("="*80)
    print(f"总文件数: {total_files}")
    print(f"  相同: {same_files} ({same_files/total_files*100:.2f}%)" if total_files > 0 else "  相同: 0")
    print(f"  不同: {different_files} ({different_files/total_files*100:.2f}%)" if total_files > 0 else "  不同: 0")
    print(f"  错误: {errors}")
    print(f"只在 new 中: {missing_in_old} 个文件")
    print(f"只在 old 中: {missing_in_new} 个文件")
    
    # 如果有不同的文件，显示详细信息
    if differences:
        print(f"\n不同文件的详细信息 ({len(differences)} 个):")
        print("-" * 80)
        for diff in differences:
            print(f"\n子文件夹: {diff['subfolder']}")
            print(f"  文件: {diff['filename']}")
            print(f"  new 路径: {diff['new_path']}")
            print(f"  old 路径: {diff['old_path']}")
            print(f"  new 大小: {diff['new_size']} 字节")
            print(f"  old 大小: {diff['old_size']} 字节")
            if diff['new_size'] != diff['old_size']:
                size_diff = diff['new_size'] - diff['old_size']
                print(f"  大小差异: {size_diff:+d} 字节")
    
    print()


if __name__ == '__main__':
    import sys
    
    # 默认使用当前目录下的 new 和 old 文件夹
    if len(sys.argv) == 1:
        # 没有参数，使用默认值
        new_dir = "new"
        old_dir = "old"
    elif len(sys.argv) == 2:
        # 只有一个参数，显示帮助信息
        print("用法: python compare_binary_files.py [new文件夹路径] [old文件夹路径]")
        print("示例: python compare_binary_files.py new old")
        print("      如果不提供参数，默认使用当前目录下的 new 和 old 文件夹")
        sys.exit(1)
    else:
        # 有2个或更多参数，使用前两个
        new_dir = sys.argv[1]
        old_dir = sys.argv[2]
    
    compare_folders(new_dir, old_dir)

