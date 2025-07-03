# ShioOfficial - 智能对话助手

## 项目简介
基于Deepseek模型的智能对话系统，支持本地和云端模型配置，提供交互式对话管理功能。

## 功能特性
✅ 多模型支持（本地/云端）
✅ 交互式配置创建向导
✅ 对话历史保存与恢复
✅ 实时分词统计
✅ 自适应温度调节

## 安装指南
```bash
# 克隆仓库
git clone https://github.com/EricJiang1329145/ShioOfficial.git

# 安装依赖
pip install -r requirements.txt
```

## 配置说明
1. 在modelSettings目录创建模型配置文件
2. 通过交互向导设置API密钥和端点
3. 修改config.ini调整运行参数

## 快速开始
```python
python main.py
```

## 技术架构
├── OpenAI SDK集成
├── JSON配置管理
├── 多线程异步处理
├── Markdown日志系统

## 贡献指南
欢迎提交PR或issue，详细请参考CONTRIBUTING.md（并不存在

## 许可证
MIT License

## 联系方式
📧 jmr_eric@outlook.com