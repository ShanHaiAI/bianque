import json
import os

from langchain_community.llms import Tongyi
from openai import OpenAI
from dotenv import load_dotenv

from core.basic_class import get_logger, log_execution_time

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

logger = get_logger()
@log_execution_time(logger)
def get_llm():
    return Tongyi( model_name="qwen-turbo",dashscope_api_key=api_key,)


class OpenAIEmbeddingModel:
    def __init__(self):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def encode(self, texts: list) -> list:
        """
        输入字符串列表，返回对应的嵌入向量列表，
        调用 OpenAI 的 text-embedding-v3 模型，返回结果为浮点型向量。
        """
        embeddings = []
        try:
            for text in texts:
                response = self.client.embeddings.create(
                    model="text-embedding-v3",
                    input=text,
                    encoding_format="float"
                )
                embedding = response.model_dump_json()
                embedding_dict = json.loads(embedding)
                embeddings.append(embedding_dict['data'][0]["embedding"])
            return embeddings
        except Exception as e:
            raise Exception("Embedding 提取失败：" + str(e))
