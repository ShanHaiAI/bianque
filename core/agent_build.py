import uuid
from typing import Annotated, List, Any, Iterator

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pandas import DataFrame
from typing_extensions import TypedDict

from core.basic_class import ShortTermMemory, LongTermMemory
from core.llm_calling import get_llm
from core.prompt import get_prompt_template
from core.tools import MilvusVectorKnowledgeBase, vector_knowledge_query


class State(TypedDict):
    messages: Annotated[List[str], add_messages]
    user_info: str
    user_id: int


class DiagnosisAgentGraph:
    def __init__(self, use_short_term_memory: bool = True, use_long_term_memory: bool = False):
        self.llm = get_llm()
        self.use_short_term_memory = use_short_term_memory
        self.use_long_term_memory = use_long_term_memory
        self.short_term_memory = ShortTermMemory() if use_short_term_memory else None
        self.long_term_memory = LongTermMemory() if use_long_term_memory else None
        self.graph = StateGraph(State)


        def rag_search(state: State) -> State:
            query_input = state["messages"][0].content
            print(query_input)
            diagnosis_kb = MilvusVectorKnowledgeBase(collection_name="diagnosis_knowledge")
            rag_result = vector_knowledge_query(query_input, diagnosis_kb)
            prompt = get_prompt_template("medical_consult").format(patient_input=query_input,
                                                                   user_info=state["user_info"], rag_result=rag_result)
            llm_response = self.llm.invoke(prompt)
            state["messages"].append(f"LLM Response: {llm_response}")
            print("LLM Response:", llm_response)
            print(state["messages"])
            return state

        def tone_rewrite_node(state: State) -> State:
            query_input = state["messages"][0].content
            last_response = state["messages"][-1].content
            print(last_response)
            patient_support_kb = MilvusVectorKnowledgeBase(collection_name="patient_support_kb")
            rag_result = vector_knowledge_query(last_response, patient_support_kb)
            prompt = get_prompt_template("tone_rewrite").format(user_input=query_input, result=last_response,
                                                                rag_result=rag_result)
            llm_response = self.llm.invoke(prompt)
            state["messages"].append(f"Final Output: {llm_response}")
            print(state)
            return state

        def update_memory_node(state: State) -> State:
            if self.use_short_term_memory:
                self.short_term_memory.add(state["user_id"], state["messages"])
            if self.use_long_term_memory:
                self.long_term_memory.add(state["user_id"], state["messages"])

            summary_prompt = "请总结以下聊天记录中的关键信息，用于更新用户健康信息：\n" + "\n".join(
                [i.content for i in state["messages"]])
            print(summary_prompt)
            summary = self.llm.invoke(summary_prompt)
            state["user_info"] = summary
            state["messages"].append(f"Memory Updated: {summary}")
            print(state["messages"])
            print(state)
            return state

        # self.graph.add_node("user_info_combine", user_info_combine)
        self.graph.add_node("rag_search", rag_search)
        self.graph.add_node("tone_rewrite", tone_rewrite_node)
        self.graph.add_node("update_memory", update_memory_node)

        self.graph.add_edge(START, "rag_search")
        self.graph.add_edge("rag_search", "tone_rewrite")
        self.graph.add_edge("tone_rewrite", "update_memory")
        self.graph.add_edge("tone_rewrite", END)

    def run(self, patient_input: str, user_id: str, user_info: DataFrame = None) -> Iterator[dict[str, Any] | Any]:
        """
        运行医疗自诊 Agent 流程

        Args:
            patient_input (str): 患者的症状描述

        Returns:
            str: 最终生成的诊断回复（包含语气改写）
        """
        prompt_template = f"Patient Input: {patient_input}"
        context = "Chat history:"
        if self.use_short_term_memory:
            context = self.short_term_memory.get_context(user_id)
        init_input = f"{context}\n{prompt_template}"
        chain = self.graph.compile()
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        output = chain.invoke(
            {"messages": init_input, "user_info": "N/A", "user_id": user_id}, config=config, stream_mode="updates"
        )
        final_output = output["tone_rewrite"]["messages"][-1]
        return final_output


# --------------------------
# ReportAgentGraph：体检报告解析 Agent
# --------------------------
class ReportAgentGraph:
    def __init__(self):
        """
        初始化体检报告解析 Agent：
            - 获取统一 LLM 实例
            - 初始化对话记忆模块
            - 构建图流程，节点顺序为：
                prepare_prompt -> mcp_rag -> llm_call -> tone_rewrite -> update_memory -> chatbot
        """
        from core.llm_calling import get_llm
        self.llm = get_llm()
        from core.basic_class import ConversationMemory
        self.memory = ConversationMemory()

        # 创建图对象
        self.graph = StateGraph(State)

        # 节点定义：与医疗自诊类似，不同在于 prompt 模板略有调整
        def prepare_prompt(state: State) -> State:
            combined = f"User Info: {state['user_info']}\n" + "\n".join(state["messages"])
            state["messages"].append(f"Prepared Report Prompt: {combined}")
            return state

        def mcp_rag_node(state: State) -> State:
            from core.mcp import rag_service
            query_input = state["messages"][-1]
            rag_result = rag_service(query_input)
            state["messages"].append(f"MCP_RAG Result: {rag_result}")
            return state

        def llm_call_node(state: State) -> State:
            prompt = "\n".join(state["messages"])
            llm_response = self.llm.call(prompt)
            state["messages"].append(f"LLM Response: {llm_response}")
            return state

        def tone_rewrite_node(state: State) -> State:
            from core.integrations.mcp import rewrite_tone
            last_response = state["messages"][-1]
            rewritten = rewrite_tone(last_response)
            state["messages"].append(f"Final Report Output: {rewritten}")
            return state

        def update_memory_node(state: State) -> State:
            summary_prompt = "请总结以下体检报告解析聊天记录中的关键信息，以更新用户体检信息：\n" + "\n".join(
                state["messages"])
            summary = self.llm.call(summary_prompt)
            state["user_info"] = summary
            state["messages"].append(f"Memory Updated: {summary}")
            return state

        def chatbot_node(state: State) -> State:
            return state

        # 统一添加节点
        self.graph.add_node("prepare_prompt", prepare_prompt)
        self.graph.add_node("mcp_rag", mcp_rag_node)
        self.graph.add_node("llm_call", llm_call_node)
        self.graph.add_node("tone_rewrite", tone_rewrite_node)
        self.graph.add_node("update_memory", update_memory_node)
        self.graph.add_node("chatbot", chatbot_node)

        # 统一连接
        self.graph.add_edge(START, "prepare_prompt")
        self.graph.add_edge("prepare_prompt", "mcp_rag")
        self.graph.add_edge("mcp_rag", "llm_call")
        self.graph.add_edge("llm_call", "tone_rewrite")
        self.graph.add_edge("tone_rewrite", "update_memory")
        self.graph.add_edge("update_memory", "chatbot")
        self.graph.add_edge("chatbot", END)

    def run(self, report_text: str) -> str:
        """
        运行体检报告解析 Agent 流程

        Args:
            report_text (str): 体检报告的文本内容（通常由 OCR 得到）

        Returns:
            str: 调整语气后的最终体检报告解析结果
        """
        prompt_template = f"Report Input: {report_text}"
        context = self.memory.get_context()
        full_input = f"{context}\n{prompt_template}" if context else prompt_template
        initial_state: State = {"messages": [full_input], "user_info": self.memory.get_context() or "N/A"}
        final_state = self.graph.run(initial_state)
        self.memory.add_interaction(report_text, final_state["messages"][-1])
        return final_state["messages"][-1]


# --------------------------
# 示例运行入口
# --------------------------
if __name__ == "__main__":
    print("=== 诊断 Agent 示例 ===")
    diag_agent = DiagnosisAgentGraph()
    diag_response = diag_agent.run("我最近连续几天发热并伴有头痛，感到非常焦虑。", '0')
    print("诊断回复：")
    print(diag_response)

    # print("\n=== 报告解析 Agent 示例 ===")
    # report_agent = ReportAgentGraph()
    # report_response = report_agent.run("体检报告显示血脂异常、血糖偏高。")
    # print("报告解析回复：")
    # print(report_response)
