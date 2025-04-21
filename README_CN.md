# 扁鹊——AI医疗自诊平台

[English Version](./README.md)

**扁鹊AI** 是一个开源项目，旨在结合先进的大语言模型（LLM）、向量数据库与智能代理架构，构建具备温度感的智能医疗自诊系统。本项目具备医学问诊、体检报告分析、文档上传与知识库构建等功能，深度集成了 MCP 平台，支持包括 Qwen、DeepSeek 等多种模型调用，并以用户关怀为核心设计理念。

---

## 目录

- [项目亮点](#项目亮点)
- [系统架构](#系统架构)
- [安装说明](#安装说明)
- [使用指南](#使用指南)
  - [启动服务](#启动服务)
  - [访问前端](#访问前端)
- [配置文件说明](#配置文件说明)
- [参与贡献](#参与贡献)
- [许可证](#许可证)

---

## 项目亮点

- 🌿 **双Agent结构**：使用LangGraph构建两个独立Agent，分别用于“医疗自诊”与“体检报告解析”。
- 🤖 **统一LLM调用接口**：通过 `get_llm()` 实现对Qwen、DeepSeek等模型的统一调用，Agent无需感知底层实现。
- 🔍 **向量知识增强**：基于Milvus构建RAG（检索增强生成）框架，上传医学文档后自动入库并用于问答检索。
- 🧾 **OCR报告识别**：使用 `pytesseract` 解析用户上传的体检报告图片内容。
- 🩺 **深度集成MCP平台**：接入MCP医疗平台，获取结构化数据增强诊断分析能力与工具调用。
- 📄 **结构化输出报告**：支持生成包含“整体评价”、“异常指标”、“原因分析”与“AI建议”的结构化医疗建议。
- 📜 **统一日志管理模块**：便于开发调试与线上追踪。
- 🐳 **支持Docker部署**：基于 Python 3.12 的容器化部署，开箱即用。

---

## 系统架构

```
project/
├── core/
│   ├── __init__.py
│   ├── basic_class.py              # 定义所有数据结构与会话记忆（含描述信息）
│   ├── agent/
│       ├── diagnosis_agent.py     # 医疗自诊相关Agent
│       └── report_agent.py        # 体检报告分析Agent
│   ├── prompt.py                  # 所有提示词统一管理
│   ├── tools.py              
│   ├── llm_calling.py             # 统一LLM与embedding服务调用逻辑
│   └── mcp.py                     # MCP平台接入逻辑
├── front/
│   └── web_ui.py                  # Gradio构建前端，包含上传构建知识库的隐藏页面
├── logger.py                      # Centralized logging module.
├── test/
├── Dockerfile                     # Dockerfile for containerized deployment (Python 3.12).
├── LICENSE
├── .env                           # 环境配置信息
└── start.py                       # 启动脚本
```

---

## 安装说明

1. **克隆项目**

   ```bash
   git clone https://github.com/your_username/bianque-ai.git
   cd bianque-ai
   ```

2. **创建虚拟环境（推荐）**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows 用户使用 `venv\Scripts\activate`
   ```

3. **安装依赖**

   确保存在 `requirements.txt` 文件，执行：

   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. **配置环境变量**

   编辑 `.env` 文件，补充 API 密钥、地址等配置项。

---

## 使用指南

### 启动服务

使用以下命令启动平台：

```bash
python start.py
```

系统会自动读取 `.env` 文件并加载前端页面。

### 访问前端

浏览器自动打开Gradio界面，包含以下模块：

- **在线智能问诊**：输入个人信息与症状进行AI辅助诊断
- **体检报告分析**：上传图片进行OCR识别并获取医学建议
- **知识库构建**（隐藏页）：上传医学文档，自动构建向量知识库（需授权）

---

## 配置文件说明

`.env` 格式如下，含注释分区：

```ini
# -----------------------------------------------------------------------------
# LLM服务配置
QWEN_API_KEY=your_qwen_api_key
QWEN_API_URL=https://api.qwen.example/llm

DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.example/llm

# -----------------------------------------------------------------------------
# MCP平台配置
MCP_API_KEY=your_mcp_api_key
MCP_API_URL=https://api.mcp.example/query
MCP_EXTRA_CONFIG=extra_value

# -----------------------------------------------------------------------------
# 向量知识库配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# -----------------------------------------------------------------------------
# 日志配置
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# 默认使用模型（qwen 或 deepseek）
SELECTED_LLM=qwen
```

---

## 参与贡献

欢迎你的贡献！

1. Fork 本仓库
2. 新建分支：`git checkout -b new-feature`
3. 提交更改：`git commit -am 'Add feature'`
4. 推送分支：`git push origin new-feature`
5. 提交 Pull Request

确保代码风格统一，并尽量添加必要的注释和测试用例。

---

## 许可证

本项目基于 [MIT License](./LICENSE) 开源发布。

---

如有建议或问题，欢迎在 GitHub 提 Issue 或 PR，一起共建扁鹊AI，为用户带来温暖且可信赖的医疗AI体验！