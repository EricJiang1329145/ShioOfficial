import os
import re


def clean_text_file(file_path):
    """
    清理文本文件中的特定符号（-、#、*）

    Args:
        file_path: 文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在！")
        return

    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 使用正则表达式删除特定符号
        cleaned_content = re.sub(r'[-#*```]', '', content)

        # 将清理后的内容写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

        print(f"已成功清理文件 {file_path} 中的符号！")

    except Exception as e:
        print(f"处理文件时出错: {e}")


if __name__ == "__main__":
    # 文件路径（假设与程序同目录）
    file_path = "prompt.txt"
    clean_text_file(file_path)