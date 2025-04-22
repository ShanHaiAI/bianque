# 扁鹊 AI：智能自诊与报告解读助手

[English README](./README.md)  
![logo](./static/banner.jpg)

**扁鹊 AI** 是一个开源项目，基于大语言模型（LLM）、向量检索（RAG）和智能体架构（LangGraph）构建，致力于提供自诊问答与医学报告分析的智能服务。通过整合 OCR 文档解析、向量数据库（Milvus）与多种 LLM 后端接口，用户可获得更专业、更可信的医疗建议。

---

## 🌟 核心特性

- 🧠 **双智能体架构**  
  - **自诊 Agent**：支持多轮对话的症状问答助手。  
  - **报告 Agent**：结合 OCR 技术自动解析上传的体检/化验报告，并给出结构化解读。

- 🔄 **基于 RAG 的知识检索**  
  通过 Milvus 向量数据库进行文档向量化与高效召回，支持上下文增强生成。

- 🧾 **OCR 文档识别集成**  
  使用 `pytesseract` 对医学报告进行文本提取。

- 🔌 **统一 LLM 接口封装**  
  通过 `get_llm()` 方法无缝切换千问、DeepSeek 等后端，无需修改核心代码。

---

## 🧬 项目结构

```
project/
├── core/
│   ├── agent_build.py         # 构建自诊与报告智能体的主逻辑。
│   ├── basic_class.py         # 核心数据结构、记忆机制等。
│   ├── prompt.py              # 提示词模板集中管理。
│   ├── tools.py               # 自定义工具类。
│   └── llm_calling.py         # 统一封装的 LLM 和 embedding 接口。
├── front/
│   └── web_ui.py              # 基于 Gradio 的前端 UI 页面。
├── logger.py                  # 日志模块。
├── test/                      # 单元测试目录。
├── Dockerfile                 # 基于 Python 3.12 的容器配置。
├── .env                       # 环境变量配置文件。
└── start.py                   # 服务启动脚本。
```

---

## ⚙️ 安装步骤

```bash
git clone https://github.com/ShanHaiAI/bianque.git
cd bianque

# 可选：创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install --no-cache-dir -r requirements.txt
```

---

## 🚀 使用指南

### ▶️ 启动服务

```bash
python start.py
```

该脚本会加载 `.env` 文件中的环境变量，并启动 Gradio 前端界面。

### 🌐 前端功能页面

- **🩺 在线自诊** – 支持对话式输入症状并获得分析建议。
- **📄 报告解读** – 上传检查报告图片，系统自动识别并解读。
- **📚 知识库构建**（隐藏页）– 供专业用户上传资料，用于构建医学知识库。

---

## 🔧 配置方法

`.env` 示例配置：

```ini
# LLM 接口配置
DASHSCOPE_API_KEY=你的千问 API Key

# 日志等级
LOG_LEVEL=INFO
```

---

## 🤝 参与贡献

欢迎社区开发者参与改进：

1. Fork 本项目  
2. 创建新分支：`git checkout -b feature/你的功能`  
3. 提交修改并 push：`git push origin feature/你的功能`  
4. 发起 Pull Request（PR）  

请确保代码风格统一，适当添加注释与测试。

---

## 📄 开源协议

本项目遵循 [MIT License](./LICENSE)。

---

💡 **扁鹊** 是中国古代著名医学家，代表精准诊断与经验智慧的象征。我们希望借助人工智能的力量，将“扁鹊之术”现代化，服务大众健康。
