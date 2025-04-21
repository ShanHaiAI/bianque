import logging
import os
from typing import Optional, List

from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS
from pydantic import BaseModel, Field

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backend")


class PatientInput(BaseModel):
    patient_id: str = Field(..., description="患者唯一标识")
    name: str = Field(..., description="患者姓名")
    age: int = Field(..., description="患者年龄")
    gender: str = Field(..., description="患者性别")
    symptoms: str = Field(..., description="患者症状描述")
    medical_history: Optional[str] = Field(None, description="患者既往病史")


class MedicalReport(BaseModel):
    patient_id: str = Field(..., description="患者唯一标识")
    report_file: str = Field(..., description="报告文件路径或 base64 数据")
    report_text: Optional[str] = Field(None, description="OCR 解析后的报告文本")


class ShortTermMemory:
    def __init__(self):
        self.memory = {}

    def add(self, user_id: str, messages: List[str]):
        if user_id not in self.memory:
            self.memory[user_id] = []
        self.memory[user_id].extend(messages)

    def get_context(self, user_id: str) -> str:
        return "\n".join(self.memory.get(user_id, []))


class LongTermMemory:
    def __init__(self):
        self.vectorstore = FAISS(embedding_function=OpenAIEmbeddings())
        self.user_indices = {}

    def add(self, user_id: str, messages: List[str]):
        docs = [Document(page_content=msg, metadata={"user_id": user_id}) for msg in messages]
        if user_id not in self.user_indices:
            self.user_indices[user_id] = self.vectorstore
        self.user_indices[user_id].add_documents(docs)

    def get_context(self, user_id: str, query: str, k: int = 3) -> str:
        if user_id not in self.user_indices:
            return ""
        docs = self.user_indices[user_id].similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in docs])


class MedicalReportOutput(BaseModel):
    """
    定义 AI 分析体检报告的输出格式

    Attributes:
        overall_evaluation (str): 对整体报告的综合评价
        abnormal_indicators (List[str]): 检测到的异常指标列表
        analysis (str): 异常指标可能原因分析
        suggestions (str): 针对异常指标给出的 AI 建议
    """
    overall_evaluation: str = Field(..., description="整体综合评价")
    abnormal_indicators: List[str] = Field(..., description="异常指标列表")
    analysis: str = Field(..., description="异常指标的原因分析")
    suggestions: str = Field(..., description="AI 给出的建议")
