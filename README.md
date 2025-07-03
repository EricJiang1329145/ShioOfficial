# TidalMind潮汐心智
[![DeepSeek Compatible](https://img.shields.io/badge/Model-DeepSeek-6C48EE)](https://github.com/deepseek-ai)
[![MacOS Ready](https://img.shields.io/badge/Mac%20Mini-M4%20Ready-00FEFF)]()

> "记忆如潮汐般涨落，而我是拾贝的少女" —— 林汐然

## 项目概述
TidalMind潮汐心智是一个基于Python实现的交互式AI对话系统，它允许用户与预设角色进行对话，并支持对话历史的保存和恢复。系统可以根据用户的选择加载不同的模型和预设角色，同时提供了丰富的工具函数来处理文件读取、时间信息获取等操作。

## 功能特性
1. **多角色预设**：提供多个预设角色，如林汐然、默认助手、技术顾问等，每个角色都有独特的性格和交互规则。
2. **对话历史管理**：支持保存和恢复对话历史，方便用户随时继续之前的对话。
3. **模型配置**：可以根据不同的模型配置文件选择使用不同的模型，如DeepSeek Reasoner等。
4. **时间信息记录**：在用户输入中自动添加当前时间信息，方便记录对话时间。
5. **错误处理**：在对话过程中出现错误时，会给出相应的错误提示，并保留最近的4条对话记录。

## 项目结构
```
TidalMind/
├── ma.py                 # 主程序文件，负责对话流程的控制
├── utils.py              # 工具函数文件，包含文件读取、时间信息获取等功能
├── prompt.txt            # 提示词预设文件，定义了各个角色的设定和交互规则
├── config.ini            # 配置文件，包含API使用的模型、流模式、温度等信息
├── modelSettings/        # 模型配置文件目录，包含不同模型的配置信息
│   ├── local_model_deepseek_r1_14b_by_ollama.txt
│   └── network_accessible_model_deepseek_reasoner_by_api.txt
├── tknz/                 # 分词器相关文件目录
└── .assistant_config/    # 配置目录，用于保存对话历史记录
    └── conversation_history.json
```

## 安装与运行
### 安装依赖
确保你已经安装了`openai`库，可以使用以下命令进行安装：
```bash
pip install openai
```

### 运行程序
在终端中运行以下命令启动程序：
```bash
python main.py
```

### 配置文件说明
- `config.ini`：可以修改该文件中的`use_model`、`use_stream`、`use_temperature`等参数来调整API的使用配置。
- `modelSettings`目录下的文件：每个文件包含一个模型的配置信息，格式为：
```
模型名称
API密钥
API基础URL
```

## 使用方法
1. **启动程序**：运行`ma.py`后，程序会尝试加载上次的对话历史。如果找到历史记录，会询问你是否恢复对话。
2. **选择预设角色**：如果没有恢复对话，程序会列出可用的预设角色，你可以输入编号选择一个角色。
3. **开始对话**：输入你的消息并按回车键发送，系统会返回相应的回复。
4. **结束对话**：输入`\bye`、`exit`或`quit`结束对话，程序会询问你是否保存当前对话。

## 示例对话
```
You：你好呀！认识一下，我是冬止无。
林汐然： “哇哦～是新朋友！(✧ω✧) 我叫林汐然，不过大家都喊我小汐～冬止无这个名字好酷哦～是取自‘冬日将尽未止’的意思嘛？(歪头思考) 对了对了，你最近有没有追什么番？我昨天刚把《更衣人偶》重刷到第三遍，缝纫机踩出火星子的那种！”
```

## 贡献
如果你对本项目感兴趣，可以通过以下方式进行贡献：
- 提交Bug报告或功能建议
- 提交代码修改或新功能实现的Pull Request

## 许可证
本项目采用[MIT许可证](LICENSE)。

## 联系方式
如果你有任何问题或建议，可以通过以下方式联系我们：
- [邮箱地址]（2900463488@qq.com）
- [项目仓库的Issues页面](https://github.com/EricJiang1329145/TidalMind/issues)