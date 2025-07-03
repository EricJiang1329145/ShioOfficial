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
# 定义一个函数，用于预处理响应
def preprocess_response(response):
    return replace_consecutive_newlines(extract_content_after_think(response)).lstrip()
# 颜色代码配置
COLOR_MAP = {
    'warning': '\033[31m',  # 红色 (警告)
    'prompt': '\033[32m',   # 绿色 (提示)
    'speech': '\033[33m',   # 黄色 (发言)
    'system': '\033[34m',   # 蓝色 (系统)
    'default': '\033[0m'    # 默认
}

def q_input(prompt: str) -> str:
    """带退出检测的输入函数"""
    # 输入提示信息
    result = input(f"{COLOR_MAP['prompt']}{prompt}\033[0m")
    # 如果输入为q，则退出程序
    if result.strip().lower() == 'q':
        raise SystemExit("返回主菜单")
    # 返回输入结果
    return result

def cprint(content: str, msg_type: str = '默认'):
    """类型化彩色打印函数"""
    # 根据msg_type获取对应的颜色
    color = COLOR_MAP.get(msg_type, COLOR_MAP['默认'])
    # 打印内容，并设置颜色
    print(f"{color}{content}\033[0m")


def read_json_config(file_path: str) -> dict:
    """
    读取并解析JSON格式的配置文件

    参数:
        file_path (str): 配置文件路径

    返回:
        dict: 解析后的配置字典

    异常:
        FileNotFoundError: 文件不存在时抛出
        json.JSONDecodeError: JSON格式错误时抛出
        KeyError: 缺少必要字段时抛出
    """
    try:
        # 打开配置文件
        with open(file_path, 'r', encoding='utf-8') as f:
            # 解析JSON文件
            config = json.load(f)
            # 检查配置文件是否包含必要字段
            if not all(k in config for k in ('model', 'api_key', 'url')):
                raise KeyError('配置文件缺少必要字段')
            # 返回解析后的配置字典
            return config
    except json.JSONDecodeError as e:
        # 打印JSON解析失败信息
        print(f"\033[31mJSON解析失败: {e}\033[0m")
        # 抛出异常
        raise

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
            cprint("错误: 文件未找到。", 'warning')
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for entry in data.get("history", []):
            if entry.get("role") == "system":
                entry["content"] = new_content
                break

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        cprint("JSON 文件已成功更新。", 'prompt')
    except json.JSONDecodeError:
        cprint("错误: 无法解析 JSON 文件。", 'warning')
    except Exception as e:
        cprint(f"错误: 发生了一个未知错误: {e}", 'warning')

def ask_user_choice(file_list):
    """
    询问用户选择使用哪个文件
    :param file_list: 可读取文件的列表
    :return: 用户选择的文件路径
    """
    if not file_list:
        cprint("未找到可读取的文件。", 'warning')
        return None
    cprint("可读取的文件有：", 'prompt')
    for i, file in enumerate(file_list, start=1):
        cprint(f"{i}. {file}", 'system')
    while True:
        try:
            choice = int(q_input("请输入要使用的文件编号: "))
            if 1 <= choice <= len(file_list):
                return file_list[choice - 1]
            else:
                cprint("输入的编号无效，请重新输入。", 'warning')
        except ValueError:
            cprint("输入无效，请输入一个数字。", 'warning')

if __name__ == "__main__":
    print("utils.py 被直接运行了。")
    from main import mainloop
    mainloop()