import sys

from openai import OpenAI

from tknz.deepseek_tokenizer import get_tokenize
from utils import *
import os


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
def selected_file() -> str:
    """
    交互式选择模型配置文件

    流程:
    1. 扫描配置目录获取可用文件列表
    2. 用户交互式选择文件
    3. 返回完整文件路径

    返回:
        str: 用户选择的配置文件绝对路径

    异常:
        FileNotFoundError: 当配置目录为空时抛出
    """
    files = search_files(config.model_settings_dir)
    selected_file = ask_user_choice(files)
    print(f"\033[31m你选择的文件是: \033[0m{selected_file}")
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
        print(f"\033[31m保存历史记录失败: \033[0m{str(e)}")


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
        print(f"\033[31m加载历史记录失败: \033[0m{str(e)}")
    return None, None


# 系统自检
def check_system_readiness():
    """系统自检功能：验证配置文件和依赖"""
    if not os.path.exists(config.model_settings_dir):
        raise FileNotFoundError(f"模型配置目录不存在: {config.model_settings_dir}")
    if not os.listdir(config.model_settings_dir):
        raise FileNotFoundError("模型配置目录为空")


# 主程序
def main():
    try:
        msd = selected_file()
        config_data = utils.read_json_config(msd)
        ums = ModelSettings(config_data['model'], config_data['api_key'], config_data['url'])
    except (FileNotFoundError, IndexError) as e:
        print(f"\033[31m配置加载失败: {e}\033[0m")
        sys.exit(1)

    while True:  # 输入验证循环
        try:
            selected = int(input("请选择预设角色（输入编号）：")) - 1
            preset_name = list(preset_prompts.keys())[selected]
            break
        except (ValueError, IndexError):
            print("\033[31m输入无效，请重新选择\033[0m")

    ums.introduce()
    use_model = ums.model
    api_key_s = ums.apiKey
    urls = ums.url

    use_stream = False
    use_temperature = 0.9
    client = OpenAI(api_key=api_key_s, base_url=urls)

    # 调用函数并传入文件名
    file_content = read_txt_file('prompt.txt')

    # 提示词预设库
    preset_prompts = {"林汐然": file_content}
    # 尝试加载历史记录
    saved_preset, saved_context = load_history()

    if saved_preset and saved_context:
        print(f"\n\033[31m找到上次的对话记录（预设角色：\033[0m{saved_preset}）")
        choice = input("\033[31m是否恢复上次对话？(\033[0my\033[31m/\033[0mn\033[31m):\033[0m ").lower()
        if choice == 'y':
            preset_name = saved_preset
            conversation_context = saved_context
            print("\033[31m对话已恢复，输入'退出'结束对话\033[0m")
            modify_json_system_content(config.HISTORY_FILE, file_content)

        else:
            saved_preset = None

    if not saved_preset:
        # 选择预设流程
        conversation_context = []
        print("\n\033[31m可用的角色预设：\033[0m")
        for i, (name) in enumerate(preset_prompts.items(), 1):
            print(f"{i}. {name}")

        selected = int(input("\033[31m请选择预设角色（输入编号）：\033[0m")) - 1
        preset_name = list(preset_prompts.keys())[selected]

    # 对话循环
    from concurrent.futures import ThreadPoolExecutor

    def process_response(response, preset_name):
        ai_response = preprocess_response(response.choices[0].message.content).lstrip()
        conversation_context.append({"role": "assistant", "content": ai_response})
        print(f"\n{preset_name}：", add_newline_after_punctuation(ai_response))
        print(get_tokenize(ai_response, config.tknz_path))

    with ThreadPoolExecutor(max_workers=4) as executor:
        while True:
            user_input = input("\n\033[36mYou：\033[0m").strip()

            if user_input.lower() in ["\\bye", "exit", "quit"]:
                save_choice = input("\033[31m是否保存当前对话？(y/n): \033[0m").lower()
                if save_choice == 'y':
                    save_history(preset_name, conversation_context)
                    print(f"\033[32m对话已保存到 {config.HISTORY_FILE}\033[30m")
                print("对话结束")
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
                print("\033[31m发生错误：\033[0m", str(e))
                conversation_context = conversation_context[-4:]


def print_welcome():
    print("欢迎使用本程序！")
    print("\033[31m这是红色文本\033[0m")
    print("\033[32m这是绿色文本\033[0m")
    print("\033[1;34m这是亮蓝色文本\033[0m")

def calculate_sum():
    total = sum(range(1, 11))
    print(f"1 到 10 的和是：{total}")


def exit_program():
    print("程序已退出。")
    sys.exit()


def perform_operation():
    operations = {
        1: print_welcome,
        2: calculate_sum,
        3 : main,
        4: exit_program
    }
    for key, value in operations.items():
        print(f"{key}. {value.__name__}")
    try:
        choice = int(input("\033[31m请输入操作对应的数字：\033[0m"))
        if choice in operations:
            result = operations[choice]()
            if result is not None:
                return
        else:
            print("\033[31m输入的数字无效，请输入有效数字。\033[0m")
    except ValueError:
        print("\033[31m输入无效，请输入一个有效的整数。\033[0m")
    perform_operation()

def mainloop():
    try:
        check_system_readiness()
        print("\033[32m系统自检通过\033[0m")
    except Exception as e:
        print(f"\033[31m系统初始化失败: {e}\033[0m")
        sys.exit(1)

    print_welcome()
    perform_operation()

if __name__ == "__main__":
    mainloop()
