import sys

import os
from utils import *

# 延迟加载大模块
def _lazy_imports():
    global OpenAI, get_tokenize, ThreadPoolExecutor
    from openai import OpenAI
    from tknz.deepseek_tokenizer import get_tokenize
    from concurrent.futures import ThreadPoolExecutor


class ConfigManager:
    """
    集中管理应用程序配置的中央控制器
    功能：
    - 管理环境变量与默认配置的优先级
    - 统一管理文件系统路径
    - 提供配置项的安全访问
    配置项说明：
    • CONFIG_DIR: 配置文件目录 (环境变量: ASSISTANT_CONFIG)
    • tknz_path: 分词器资源路径
    • HISTORY_FILE: 对话历史存储路径
    • model_settings_dir: 模型配置目录 (环境变量: MODEL_SETTINGS_DIR)
    使用示例：
    >>> config = ConfigManager()
    >>> print(config.HISTORY_FILE)
    """
    # 初始化ConfigManager类
    def __init__(self):
        # 获取环境变量ASSISTANT_CONFIG的值，如果没有设置，则默认为.assistant_config
        self.CONFIG_DIR = os.getenv('ASSISTANT_CONFIG', '.assistant_config')
        # 获取当前文件所在目录，并拼接上tknz目录，得到tknz_path
        self.tknz_path = os.path.join(os.path.dirname(__file__), 'tknz')
        # 将CONFIG_DIR和conversation_history.json拼接，得到HISTORY_FILE
        self.HISTORY_FILE = os.path.join(self.CONFIG_DIR, 'conversation_history.json')
        # 获取环境变量MODEL_SETTINGS_DIR的值，如果没有设置，则默认为modelSettings
        self.model_settings_dir = os.getenv('MODEL_SETTINGS_DIR', 'modelSettings')

config = ConfigManager()
_CONFIG_CACHE = {'files': None, 'mtime': 0}

def selected_file() -> str:
    """
    交互式选择模型配置文件（带缓存机制）

    优化点:
    • 缓存文件列表和最后修改时间
    • 仅当目录变更时重新扫描
    """
    current_mtime = os.path.getmtime(config.model_settings_dir)
    if not _CONFIG_CACHE['files'] or current_mtime > _CONFIG_CACHE['mtime']:
        _CONFIG_CACHE['files'] = search_files(config.model_settings_dir)
        _CONFIG_CACHE['mtime'] = current_mtime
    
    selected_file = ask_user_choice(_CONFIG_CACHE['files'])
    cprint(f"你选择的文件是:{os.path.basename(selected_file)}", 'prompt')
    return selected_file


class ModelSettings:
    """模型配置信息容器

    属性:
        model (str): 模型标识名称
        apiKey (str): API访问密钥
        url (str): 服务端点URL

    示例:
        >>> settings = ModelSettings('deepseek', 'sk-xxx', 'https://api.deepseek.com')
    """
    def __init__(self, model: str, api_key: str, url: str):
        self.model = model
        self.apiKey = api_key
        self.url = url

    def introduce(self) -> None:
        """打印模型配置概要信息

        输出格式:
            [模型名称] [API密钥掩码] [服务端点]
            示例: deepseek sk-***3 https://api.deepseek.com
        """
        print(self.model, self.apiKey, self.url)



# 初始化配置目录
def init_config():
    if not os.path.exists(config.CONFIG_DIR):
        os.makedirs(config.CONFIG_DIR)


# 保存对话上下文
from threading import Lock
import queue

history_cache = {}
file_lock = Lock()
log_queue = queue.Queue()

def async_writer():
    while True:
        item = log_queue.get()
        if item is None:
            break
        preset, ctx = item
        with file_lock:
            with open(config.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump({"preset": preset, "history": ctx}, f, ensure_ascii=False, indent=2)

from threading import Thread
writer_thread = Thread(target=async_writer, daemon=True)
writer_thread.start()

def save_history(preset_name, context):
    init_config()
    global history_cache
    history_cache = {'preset': preset_name, 'history': context}
    try:
        log_queue.put((preset_name, context))
    except Exception as e:
        cprint(f"保存历史记录失败: {str(e)}",'warning')


# 加载历史记录
def load_history():
    global history_cache
    if history_cache:
        return history_cache.get('preset'), history_cache.get('history')
    try:
        if os.path.exists(config.HISTORY_FILE):
            with open(config.HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history_cache.update(data)
                return data['preset'], data['history']
    except Exception as e:
        cprint(f"加载历史记录失败: {str(e)}",'warning')
    return None, None


# 系统自检
def check_system_readiness():
    """系统自检功能：验证配置文件和依赖"""
    if not os.path.exists(config.model_settings_dir):
        raise FileNotFoundError(f"模型配置目录不存在: {config.model_settings_dir}")
    if not os.listdir(config.model_settings_dir):
        raise FileNotFoundError("模型配置目录为空")


# 主程序
# 缓存模型配置
_MODEL_CACHE = {}

def main():
    try:
        # 获取选择的文件
        msd = selected_file()
        # 如果选择的文件不在缓存中，则读取配置文件并创建模型设置
        if msd not in _MODEL_CACHE:
            # 读取msd路径下的json配置文件
            config_data = read_json_config(msd)
            # 将模型设置缓存到_MODEL_CACHE字典中，键为msd，值为ModelSettings对象，参数为config_data字典中的model、api_key和url
            _MODEL_CACHE[msd] = ModelSettings(config_data['model'], config_data['api_key'], config_data['url'])
        # 获取模型设置
        ums = _MODEL_CACHE[msd]
    except (FileNotFoundError, IndexError, ValueError) as e:
        # 如果发生错误，则打印错误信息并退出程序
        cprint(f"配置加载失败: {e}", 'warning')
        sys.exit(1)

    while True:  # 输入验证循环
        try:
            # 获取用户输入的角色编号
            selected = int(input("请选择预设角色（输入编号）：")) - 1
            # 获取对应角色的预设名称
            preset_name = list(preset_prompts.keys())[selected]
            break
        except (ValueError, IndexError):
            # 如果输入无效，则打印提示信息
            cprint("输入无效，请重新选择", 'warning')

    # 介绍角色
    ums.introduce()
    # 获取模型、API密钥和URL
    use_model = ums.model
    api_key_s = ums.apiKey
    urls = ums.url

    use_stream = False
    use_temperature = 0.9
    # 创建OpenAI客户端
    client = OpenAI(api_key=api_key_s, base_url=urls)

    # 调用函数并传入文件名
    file_content = read_txt_file('prompt.txt')

    # 提示词预设库
    preset_prompts = {"林汐然": file_content}
    # 尝试加载历史记录
    saved_preset, saved_context = load_history()

    if saved_preset and saved_context:
        # 如果找到历史记录，则打印提示信息并询问用户是否恢复
        cprint(f"找到上次的对话记录（预设角色：{saved_preset}", 'system')
        cprint("是否恢复上次对话？(y/n):",'speech')
        choice = input().lower()
        if choice == 'y':
            # 如果用户选择恢复，则恢复对话并修改JSON文件
            preset_name = saved_preset
            conversation_context = saved_context
            cprint("对话已恢复，输入'退出'结束对话",'prompt')
            modify_json_system_content(config.HISTORY_FILE, file_content)

        else:
            # 如果用户选择不恢复，则清空历史记录
            saved_preset = None

    if not saved_preset:
        # 选择预设流程
        conversation_context = []
        cprint("可用的角色预设：",'system')
        for i, (name) in enumerate(preset_prompts.items(), 1):
            print(f"{i}. {name}")

        selected = int(q_input("请选择预设角色（输入编号）：")) - 1
        preset_name = list(preset_prompts.keys())[selected]

    # 对话循环
    from concurrent.futures import ThreadPoolExecutor

    def process_response(response, preset_name):
        ai_response = preprocess_response(response.choices[0].message.content).lstrip()
        conversation_context.append({"role": "assistant", "content": ai_response})
        cprint(f"{preset_name}：{add_newline_after_punctuation(ai_response)}", 'speech')
        print(get_tokenize(ai_response, config.tknz_path))

    _lazy_imports()  # 实际需要时加载
    with ThreadPoolExecutor(max_workers=2) as executor:  # 减少初始线程数
        while True:
            user_input = q_input("\nYou：").strip()

            if user_input.lower() in ["\\bye", "exit", "quit"]:
                cprint("是否保存当前对话？(y/n): ",'speech')
                save_choice = input().lower()
                if save_choice == 'y':
                    save_history(preset_name, conversation_context)
                    cprint(f"对话已保存到 {config.HISTORY_FILE}",'prompt')
                cprint("对话结束", 'prompt')
                break

            user_input += get_current_time_info()
            print(get_tokenize(user_input, config.tknz_path))
            conversation_context.append({"role": "user", "content": user_input})

            try:
                future = executor.submit(
                    client.chat.completions.create,
                    model=use_model,
                    messages=conversation_context,
                    stream=use_stream,
                    temperature=use_temperature
                )
                future.add_done_callback(lambda f: process_response(f.result(), preset_name))
            except Exception as e:
                cprint(f"发生错误：{str(e)}", 'warning')
                conversation_context = conversation_context[-4:]


def print_welcome():
    cprint("欢迎使用本程序！")
    cprint("这是红色文本",'warning')
    cprint("这是绿色文本",'prompt')
    cprint("这是亮蓝色文本",'system')

def calculate_sum():
    total = sum(range(1, 11))
    print(f"1 到 10 的和是：{total}")


def exit_program():
    print("程序已退出。")
    sys.exit()


def perform_operation():
    # 定义一个字典，用于存储操作和对应的函数
    operations = {
        1: print_welcome,
        2: calculate_sum,
        3: main,
        4: switch_cprint,
        5: exit_program
    }
    # 遍历字典，打印操作和对应的函数名
    for key, value in operations.items():
        print(f"{key}. {value.__name__}")
    # 尝试获取用户输入的操作数字
    try:
        cprint("请输入操作对应的数字：","speech")
        choice = int(input())
        # 判断用户输入的数字是否在字典中
        if choice in operations:
            # 调用对应的函数
            result = operations[choice]()
            # 如果函数返回结果不为空，则返回
            if result is not None:
                return
        else:
            # 如果用户输入的数字不在字典中，则打印错误信息
            cprint("输入的数字无效，请输入有效数字。",'warning')
    except ValueError:
        # 如果用户输入的不是整数，则打印错误信息
        cprint("输入无效，请输入一个有效的整数。",'warning')
    # 递归调用perform_operation函数，重新开始
    perform_operation()

def mainloop():
    # 延迟系统检查到实际需要时
    print_welcome()
    try:
        perform_operation()
    except Exception as e:
        check_system_readiness()  # 实际出错时才执行完整检查
        cprint(f"运行时错误: {e}",'warning')
        sys.exit(1)

if __name__ == "__main__":
    mainloop()
