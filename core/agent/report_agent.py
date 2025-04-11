import os
from core.llm_calling import QwenLLM
from core.prompt import get_prompt_template
from core.basic_class import ConversationMemory
from core.integrations.mcp import query_mcp_data
from rag_tool import vector_knowledge_query

class ReportAgent:
    def __init__(self):
        self.llm = QwenLLM()
        self.memory = ConversationMemory()

    def run(self, report_text: str) -> str:
        # 使用专用于报告分析的 prompt 模板
        prompt_template = get_prompt_template("report_analysis")
        prompt = prompt_template.format(report_text=report_text)
        context = self.memory.get_context()
        full_prompt = context + "\n" + prompt if context else prompt

        mcp_result = query_mcp_data(report_text)
        rag_result = vector_knowledge_query(report_text)
        enriched_prompt = full_prompt + f"\nMCP 查询结果：{mcp_result}\nRAG 检索结果：{rag_result}"

        response = self.llm.call(enriched_prompt)
        self.memory.add_interaction(report_text, response)
        return response

if __name__ == "__main__":
    agent = ReportAgent()
    sample_report = "体检报告显示血脂异常，血糖偏高。"
    print("报告解析结果：", agent.run(sample_report))
