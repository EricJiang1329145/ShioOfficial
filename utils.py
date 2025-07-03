import datetime
import os
import json
import re


def replace_consecutive_newlines(input_string):
    pattern = r'\n{2,}'
    return re.sub(pattern, '\n', input_string)


def get_current_time_info():
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 格式化日期和时间
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    # 获取星期信息
    weekday_mapping = {
        0: "星期一",
        1: "星期二",
        2: "星期三",
        3: "星期四",
        4: "星期五",
        5: "星期六",
        6: "星期日"
    }
    weekday = weekday_mapping[current_time.weekday()]
    # 组合输出信息
    result = f"{formatted_time} {weekday}"
    return "["+result+"]"

def extract_content_after_think(input_str):
    # 查找 </think> 的位置
    index = input_str.find("</think>")
    if index != -1:
        # 如果找到 </think>，则返回其后的部分
        return input_str[index + len("</think>"):]
    else:
        # 如果未找到 </think>，则返回原始字符串
        return input_str
# 定义一个函数，用于预处理响应
def preprocess_response(response):
    return replace_consecutive_newlines(extract_content_after_think(response)).lstrip()
def read_txt_file(file_name):
    try:
        # 使用with语句打开文件
        with open(file_name, 'r', encoding='utf-8') as file:
            # 读取整个文件内容到变量中
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 {file_name} 未找到。\n")
        return None
    except Exception as e:
        print(f"读取文件时出现错误: {e}\n")
        return None

def add_newline_after_punctuation(text):
    # 定义需要添加换行符的标点符号
    punctuation = '，。！？；：、.,…）'
    result = ""
    consecutive_punctuation = ""
    for char in text:
        if char in punctuation:
            consecutive_punctuation += char
        else:
            if consecutive_punctuation:
                result += consecutive_punctuation + '\n'
                consecutive_punctuation = ""
            result += char
    # 处理字符串结尾的连续标点符号
    if consecutive_punctuation:
        result += consecutive_punctuation + '\n'
    return result

def read_specific_line(file_path, line_number):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, start=1):
                if i == line_number:
                    return line.strip()
            return None
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到。")
    except Exception as e:
        print(f"错误: 发生未知错误 - {e}")
    return None

def search_files(directory):
    """
    搜索指定目录下所有可读取的文件
    :param directory: 要搜索的目录
    :return: 可读取文件的列表
    """
    file_list = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        file_list.append(file_path)
                except Exception:
                    continue
    return file_list

def modify_json_system_content(file_path, new_content):
    try:
        if not os.path.exists(file_path):
            print("错误: 文件未找到。")
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data.get("history", []):
            if entry.get("role") == "system":
                entry["content"] = new_content
                break

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print("JSON 文件已成功更新。")
    except json.JSONDecodeError:
        print("错误: 无法解析 JSON 文件。")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")

def ask_user_choice(file_list):
    """
    询问用户选择使用哪个文件
    :param file_list: 可读取文件的列表
    :return: 用户选择的文件路径
    """
    if not file_list:
        print("未找到可读取的文件。")
        return None
    print("可读取的文件有：")
    for i, file in enumerate(file_list, start=1):
        print(f"{i}. {file}")
    while True:
        try:
            choice = int(input("请输入要使用的文件编号: "))
            if 1 <= choice <= len(file_list):
                return file_list[choice - 1]
            else:
                print("输入的编号无效，请重新输入。")
        except ValueError:
            print("输入无效，请输入一个数字。")
