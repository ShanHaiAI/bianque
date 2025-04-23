import logging
import os
import time
from datetime import datetime
from enum import Enum
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import List
from typing import Optional

from langchain.schema import Document
# from langchain.vectorstores import FAISS
from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    def __init__(
            self,
            log_level: LogLevel = LogLevel.INFO,
            console_output: bool = True,
            file_output: bool = False,
            log_dir: str = "./log",
            max_file_size: int = 5,
            backup_count: int = 3,
            log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    ):
        self.log_level = getattr(logging, log_level.upper())
        self.console_output = console_output
        self.file_output = file_output
        self.log_dir = log_dir
        self.max_file_size = max_file_size * 1024 * 1024  # MB to bytes
        self.backup_count = backup_count
        self.log_format = log_format
        self.log_file = self._generate_log_filename()

    def _generate_log_filename(self) -> str:
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_dir, f"log_{timestamp}.log")

    def initialize_logger(self, logger_name: str = "app") -> logging.Logger:
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)

        # 清理旧的 handler，避免重复输出
        if logger.hasHandlers():
            logger.handlers.clear()

        formatter = logging.Formatter(self.log_format)

        if self.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if self.file_output:
            file_handler = RotatingFileHandler(
                self.log_file, maxBytes=self.max_file_size, backupCount=self.backup_count
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.propagate = False
        return logger


def get_logger(
        log_level: LogLevel = LogLevel.INFO,
        console_output: bool = True,
        file_output: bool = False,
        log_dir: str = "./log",
        max_file_size: int = 5,
        backup_count: int = 3,
        log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """
    获取统一格式的 logger，日志文件将保存至 ./log/log_时间戳.log
    """
    return Logger(
        log_level=log_level,
        console_output=console_output,
        file_output=file_output,
        log_dir=log_dir,
        max_file_size=max_file_size,
        backup_count=backup_count,
        log_format=log_format
    ).initialize_logger()


def log_execution_time(logger: logging.Logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"函数 {func.__name__} 执行时间: {elapsed:.2f} 秒")
            return result

        return wrapper

    return decorator



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
        messages_list = []
        print(messages)
        for message in messages:
            messages_list.append(message.content)
        self.memory[user_id].extend(messages_list)

    def get_context(self, user_id: str) -> str:
        return "\n".join(str(self.memory.get(user_id, [])))


class LongTermMemory:
    def __init__(self):
        #self.vectorstore = FAISS(embedding_function=OpenAIEmbeddings())
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
