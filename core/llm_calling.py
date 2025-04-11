import os
import requests
from typing import Optional, List
from sentence_transformers import SentenceTransformer


# -----------------------------------------------------------------------------
# Qwen LLM 封装
class QwenLLM:
    """
    Qwen LLM 调用封装

    Attributes:
        api_url (str): Qwen API 请求地址
        api_key (str): Qwen API key
    """
    api_url: str = os.getenv("QWEN_API_URL", "https://api.qwen.example/llm")
    api_key: str = os.getenv("QWEN_API_KEY", "your_qwen_api_key")

    def call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        调用 Qwen LLM 模型生成回答

        Args:
            prompt (str): 输入提示
            stop (Optional[List[str]]): 可选的终止符列表

        Returns:
            str: 模型生成的回答文本

        Raises:
            Exception: 请求失败时抛出异常
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {"prompt": prompt, "stop": stop}
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.ok:
            return response.json().get("result", "")
        else:
            raise Exception("调用 Qwen API 失败: " + response.text)


# -----------------------------------------------------------------------------
# DeepSeek LLM 封装（示例）
class DeepSeekLLM:
    """
    DeepSeek LLM 调用封装

    Attributes:
        api_url (str): DeepSeek API 请求地址
        api_key (str): DeepSeek API key
    """
    api_url: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.example/llm")
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key")

    def call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {"prompt": prompt, "stop": stop}
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.ok:
            return response.json().get("result", "")
        else:
            raise Exception("调用 DeepSeek API 失败: " + response.text)


# -----------------------------------------------------------------------------
# Embedding 封装（基于 SentenceTransformer）
class EmbeddingModel:
    """
    Embedding 模型，用于生成文本向量

    Args:
        model_name (str): 使用的模型名称 (默认 all-MiniLM-L6-v2)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        对输入文本列表生成向量表示

        Args:
            texts (List[str]): 待向量化的文本列表

        Returns:
            List[List[float]]: 每个文本对应的向量列表
        """
        return self.model.encode(texts).tolist()


# -----------------------------------------------------------------------------
# 封装一个统一获取 LLM 实例的方法，实现 agent 对 LLM 调用无感知
def get_llm():
    """
    根据环境变量 SELECTED_LLM 返回对应的 LLM 实例

    Returns:
        一个具备 call(prompt, stop) 方法的 LLM 实例
    """
    selected = os.getenv("SELECTED_LLM", "qwen").lower()
    if selected == "qwen":
        return QwenLLM()
    elif selected == "deepseek":
        return DeepSeekLLM()
    else:
        raise ValueError("不支持的 LLM 类型，请检查 SELECTED_LLM 配置")
