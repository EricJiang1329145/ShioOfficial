# 初始化设置
settings = {
    "use_stream": False,
    "use_temperature": 0.9
}


def show_menu():
    print("请选择操作：")
    print("1. 查看当前设置")
    print("2. 修改设置")
    print("3. 执行其他操作")
    print("4. 退出程序")


def view_settings():
    print("当前设置如下：")
    for key, value in settings.items():
        print(f"{key}: {value}")


def modify_settings():
    print("可修改的设置项：")
    for index, key in enumerate(settings.keys(), start=1):
        print(f"{index}. {key}")
    choice = input("请输入要修改的设置项序号：")
    try:
        choice = int(choice)
        if 1 <= choice <= len(settings):
            key = list(settings.keys())[choice - 1]
            new_value = input(f"请输入 {key} 的新值：")
            settings[key] = new_value
            print(f"{key} 已修改为 {new_value}")
        else:
            print("无效的序号，请重新输入。")
    except ValueError:
        print("输入无效，请输入数字序号。")


def other_operation():
    print("执行其他操作...")


def main():
    while True:
        show_menu()
        choice = input("请输入操作序号：")
        if choice == "1":
            view_settings()
        elif choice == "2":
            modify_settings()
        elif choice == "3":
            other_operation()
        elif choice == "4":
            print("退出程序。")
            break
        else:
            print("无效的操作序号，请重新输入。")


if __name__ == "__main__":
    main()
