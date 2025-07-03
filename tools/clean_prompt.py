import os
import re
import sys
sys.path.append('/Users/ericjiang/Desktop/pgms/ShioOfficial')
from utils import cprint

def clean_prompt_file():
    """
    清理prompt.txt中的多余换行
    功能：
    - 替换连续多个换行符为单个换行
    - 去除行尾换行符
    - 保留文件原始编码（UTF-8）
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'prompt.txt')
    
    if not os.path.exists(file_path):
        cprint(f"文件不存在: {file_path}", 'warning')
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 统计原始换行数
        original_lines = content.count('\n')
        
        # 替换连续换行符（至少2个）为单个换行
        cleaned = re.sub(r'\n{2,}', '\n', content)
        # 去除最后一行换行符
        cleaned = cleaned.rstrip('\n') + '\n'

        # 写入处理后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)

        # 统计处理结果
        new_lines = cleaned.count('\n')
        cprint(f"清理完成 原始行数: {original_lines} → 当前行数: {new_lines}", 'system')

    except Exception as e:
        cprint(f"处理失败: {str(e)}", 'warning')

if __name__ == '__main__':
    clean_prompt_file()