import logging
import os
from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from typing import Optional, List
from typing import Optional, List

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


class ConversationMemory:
    """
    对话记忆模块，用于记录和构建多轮对话上下文
    """

    def __init__(self):
        self.history: List[dict] = []

    def add_interaction(self, user_input: str, agent_response: str):
        self.history.append({"user": user_input, "agent": agent_response})

    def get_context(self) -> str:
        context = ""
        for interaction in self.history:
            context += f"患者：{interaction['user']}\n系统：{interaction['agent']}\n"
        return context

    def clear(self):
        self.history = []


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
