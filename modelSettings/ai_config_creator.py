import json
import os
from typing import Tuple

def get_valid_input(prompt: str, required: bool = True) -> str:
    """获取有效用户输入"""
    while True:
        value = input(prompt).strip()
        if not value and required:
            print("\033[33m此为必填项，请重新输入！\033[0m")
            continue
        return value

def generate_filename(model_name: str) -> str:
    """生成规范化的配置文件名"""
    base_name = model_name.split(':')[0].replace(' ', '_').replace('/', '-')
    return f"{base_name}_config.json"

def create_ai_config() -> Tuple[bool, str]:
    """交互式创建AI配置文件"""
    try:
        print("\n\033[36m=== AI配置创建向导 ===\033[0m")
        
        config = {
            "model": get_valid_input("模型名称/标识符（必填）: "),
            "api_key": get_valid_input("API密钥（留空则跳过）: ", required=False),
            "url": get_valid_input("API端点URL（必填）: ")
        }

        # 生成目标路径
        filename = generate_filename(config['model'])
        save_path = os.path.join(os.path.dirname(__file__), filename)

        # 避免覆盖已有文件
        if os.path.exists(save_path):
            choice = input(f"文件 {filename} 已存在，覆盖？(y/n): ").lower()
            if choice != 'y':
                return False, "用户取消操作"

        with open(save_path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return True, save_path

    except (PermissionError, IsADirectoryError) as e:
        return False, f"文件保存失败: {str(e)}"
    except KeyboardInterrupt:
        print("\n\033[33m操作已中止\033[0m")
        return False, "用户中断"

if __name__ == "__main__":
    success, result = create_ai_config()
    if success:
        print(f"\n\033[32m✔ 配置文件已创建: {result}\033[0m")
    else:
        print(f"\n\033[31m✘ 创建失败: {result}\033[0m")