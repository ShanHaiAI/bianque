# Bian Que：A AI Medical Self-Diagnosis Agent

[中文版本](./README_CN.md)

Bian Que AI is an open-source project that leverages cutting-edge LLM technologies, vector databases, and advanced agent architectures to provide an AI-powered medical self-diagnosis and report analysis platform. The project combines robust tools such as OCR for document parsing, RAG (Retrieval-Augmented Generation) using Milvus for vector-based knowledge retrieval, and multiple LLM backends (e.g., Qwen, DeepSeek) with a unified interface. Additionally, deep integration with MCP (Medical Care Platform) enriches the diagnostic insights with external medical data.

---

## Table of Contents

- [Features](#features)
- [Project Architecture](#project-architecture)
- [Installation](#installation)
- [Usage](#usage)
  - [Starting the Service](#starting-the-service)
  - [Accessing the Frontend](#accessing-the-frontend)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Dual Agent Architecture**: Two separate agents are available – one for medical self-diagnosis and another for report analysis – built with a robust agent framework (based on LangGraph).
- **Unified LLM Interface**: Use a unified API via `get_llm()` to seamlessly switch between different LLM backends (e.g., Qwen, DeepSeek) without changing agent code.
- **RAG-based Knowledge Retrieval**: Integrates a vector database (Milvus) for document embedding and retrieval to support augmented generation.
- **OCR Integration**: Extract text from medical reports using `pytesseract`.
- **Deep MCP Integration**: Deeply integrate with MCP to retrieve structured and enriched external medical data for enhanced diagnostic accuracy.
- **Structured Reporting Output**: Automatically generate detailed medical report outputs including overall evaluation, abnormal indicators, analysis, and AI suggestions.
- **Centralized Logging**: A dedicated logging module for consistent and comprehensive background logging.
- **Dockerized Deployment**: Includes a Dockerfile for containerized deployment using Python 3.12.

---

## Project Architecture

```
project/
├── core/
│   ├── __init__.py
│   ├── basic_class.py             # Pydantic models with detailed field descriptions and conversation memory.
│   ├── agent/
│       ├── diagnosis_agent.py     # Agent dedicated to medical self-diagnosis.
│       └── report_agent.py        # Agent for medical report analysis.
│   ├── prompt.py                  # Centralized prompt templates for LLM guidance.
│   ├── tools.py              
│   ├── llm_calling.py             # Unified LLM and embedding API, supporting Qwen, DeepSeek, etc.
│   └── mcp.py                     # MCP platform integration for medical data and tool calls.
├── front/
│   └── web_ui.py                  # Frontend built with Gradio, including a hidden page for uploading documents to build the knowledge base.
├── logger.py                      # Centralized logging module.
├── test/
├── Dockerfile                     # Dockerfile for containerized deployment (Python 3.12).
├── LICENSE
├── .env                           # Environment configuration file.
└── start.py                       # Python startup script.
```

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your_username/bianque-ai.git
   cd bianque-ai
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   Ensure you have a `requirements.txt` file in the repository with all required dependencies. Then run:

   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. **Configure Environment Variables**

   Edit the `.env` file to include your API keys, URLs, and other configurations as shown below.

---

## Usage

### Starting the Service

Run the project using the provided Python startup script:

```bash
python start.py
```

This command automatically loads environment variables from the `.env` file and starts the Gradio frontend service.

### Accessing the Frontend

The Gradio interface will launch automatically and be accessible via your browser. It includes the following tabs:
- **Online Diagnosis**: For patients to input their symptoms.
- **Report Analysis**: To upload images for OCR-based report analysis.
- **Knowledge Base Construction**: (Hidden page) For authorized users to upload professional documents and build the vector-based knowledge base.

---

## Configuration

The `.env` file is organized as follows:

```ini
# .env

# -----------------------------------------------------------------------------
# LLM Service Configuration
QWEN_API_KEY=your_qwen_api_key
QWEN_API_URL=https://api.qwen.example/llm

DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.example/llm

# -----------------------------------------------------------------------------
# MCP Platform Configuration
MCP_API_KEY=your_mcp_api_key
MCP_API_URL=https://api.mcp.example/query
MCP_EXTRA_CONFIG=extra_value

# -----------------------------------------------------------------------------
# Vector Knowledge Base (Milvus) Configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530

# -----------------------------------------------------------------------------
# Logging Configuration
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# LLM Selection: Options are 'qwen' or 'deepseek'
SELECTED_LLM=qwen
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes.
4. Push to your fork (`git push origin feature-branch`).
5. Open a pull request.

Ensure your changes adhere to the project's coding style and include appropriate documentation and unit tests.

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

Feel free to reach out via GitHub issues or pull requests if you have any questions or suggestions. Enjoy using **Bian Que AI** for intelligent and supportive medical self-diagnosis!
