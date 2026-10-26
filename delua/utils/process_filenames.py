import os
import sys

def process_filenames(folder_path, output_file='output.txt'):
    """
    读取指定文件夹下所有文件名，用_拆分后只保留第三个部分，去重后输出到文件
    
    Args:
        folder_path: 要处理的文件夹路径
        output_file: 输出文件名，默认为output.txt
    """
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        print(f"错误：文件夹 '{folder_path}' 不存在！")
        return
    
    # 获取文件夹下所有文件名
    try:
        filenames = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except PermissionError:
        print(f"错误：没有权限访问文件夹 '{folder_path}'！")
        return
    
    if not filenames:
        print(f"警告：文件夹 '{folder_path}' 中没有文件！")
        return
    
    # 处理文件名
    processed_names = set()  # 使用set自动去重
    for filename in filenames:
        # 用_拆分文件名
        parts = filename.split('_')
        
        # 如果拆分后少于3个部分，跳过
        if len(parts) < 3:
            print(f"警告：文件名 '{filename}' 拆分后少于3个部分，跳过")
            continue
        
        # 只保留第三个字符串（索引为2）
        processed_name = parts[2]
        
        # 如果以.lua结尾，去掉.lua扩展名
        if processed_name.endswith('.lua'):
            processed_name = processed_name[:-4]  # 去掉最后4个字符".lua"
        
        processed_names.add(processed_name)
    
    # 将set转换为排序后的列表，以便输出顺序一致
    processed_names_sorted = sorted(processed_names)
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for name in processed_names_sorted:
                f.write(name + '\n')
        print(f"成功处理 {len(processed_names_sorted)} 个不重复的文件名，结果已保存到 '{output_file}'")
    except Exception as e:
        print(f"错误：写入文件时出错 - {e}")

if __name__ == '__main__':
    # 如果通过命令行参数传入文件夹路径
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.txt'
    else:
        # 交互式输入
        folder_path = input("请输入要处理的文件夹路径: ").strip()
        output_file = input("请输入输出文件名（直接回车使用默认output.txt）: ").strip()
        if not output_file:
            output_file = 'output.txt'
    
    process_filenames(folder_path, output_file)
#python process_filenames.py "C:\Users\Administrator\Desktop\1202" "C:\Users\Administrator\Desktop\1202\output.txt"


