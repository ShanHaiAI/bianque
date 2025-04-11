import os
from core.llm_calling import QwenLLM
from core.prompt import get_prompt_template
from core.basic_class import ConversationMemory
from core.integrations.mcp import query_mcp_data
from rag_tool import vector_knowledge_query  # 从独立文件调用

# 假设 langgraph 提供类似接口，我们用伪代码示例 agent 实现
class DiagnosisAgent:
    def __init__(self):
        self.llm = QwenLLM()  # 可配置成 DeepSeekLLM 等
        self.memory = ConversationMemory()

    def run(self, patient_input: str) -> str:
        # 获取 prompt 模板并格式化
        prompt_template = get_prompt_template("medical_consult")
        prompt = prompt_template.format(patient_input=patient_input)
        # 可选：整合内存上下文
        context = self.memory.get_context()
        full_prompt = context + "\n" + prompt if context else prompt

        # 执行 MCP 和 RAG 查询以丰富 prompt（示例拼接查询结果）
        mcp_result = query_mcp_data(patient_input)
        rag_result = vector_knowledge_query(patient_input)
        enriched_prompt = full_prompt + f"\nMCP 查询结果：{mcp_result}\nRAG 检索结果：{rag_result}"

        # 调用 LLM 生成回答
        response = self.llm.call(enriched_prompt)
        # 将本次对话加入记忆
        self.memory.add_interaction(patient_input, response)
        return response

if __name__ == "__main__":
    agent = DiagnosisAgent()
    sample = "我最近连续几天发热并伴有头痛，非常焦虑。"
    print("诊断回复：", agent.run(sample))
