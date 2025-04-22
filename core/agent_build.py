import uuid
from typing import Annotated, List, Any, Iterator

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from core.basic_class import ShortTermMemory, LongTermMemory, get_logger, log_execution_time
from core.llm_calling import get_llm
from core.prompt import get_prompt_template
from core.tools import MilvusVectorKnowledgeBase, vector_knowledge_query

logger = get_logger()


class State(TypedDict):
    messages: Annotated[List[str], add_messages]
    user_info: str
    user_id: int


class DiagnosisAgentGraph:
    """

    """
    def __init__(self, use_short_term_memory: bool = True, use_long_term_memory: bool = False):
        self.llm = get_llm()
        self.use_short_term_memory = use_short_term_memory
        self.use_long_term_memory = use_long_term_memory
        self.short_term_memory = ShortTermMemory() if use_short_term_memory else None
        self.long_term_memory = LongTermMemory() if use_long_term_memory else None
        self.graph = StateGraph(State)

        @log_execution_time(logger)
        def rag_search(state: State) -> State:
            query_input = state["messages"][0].content
            diagnosis_kb = MilvusVectorKnowledgeBase(collection_name="diagnosis_knowledge")
            rag_result = vector_knowledge_query(query_input, diagnosis_kb)
            prompt = get_prompt_template("medical_consult").format(patient_input=query_input,
                                                                   user_info=state["user_info"], rag_result=rag_result)
            llm_response = self.llm.invoke(prompt)
            state["messages"].append(f"LLM Response: {llm_response}")
            logger.info(llm_response)
            return state

        @log_execution_time(logger)
        def tone_rewrite_node(state: State) -> State:
            query_input = state["messages"][0].content
            last_response = state["messages"][-1].content
            patient_support_kb = MilvusVectorKnowledgeBase(collection_name="patient_support_kb")
            rag_result = vector_knowledge_query(last_response, patient_support_kb)
            prompt = get_prompt_template("tone_rewrite").format(user_input=query_input, result=last_response,
                                                                rag_result=rag_result)
            llm_response = self.llm.invoke(prompt)
            state["messages"].append(f"Final Output: {llm_response}")
            logger.info(llm_response)
            return state

        @log_execution_time(logger)
        def update_memory_node(state: State) -> State:
            if self.use_short_term_memory:
                self.short_term_memory.add(state["user_id"], state["messages"])
            if self.use_long_term_memory:
                self.long_term_memory.add(state["user_id"], state["messages"])

            # summary_prompt = "请总结以下聊天记录中的关键信息，用于更新用户健康信息：\n" + "\n".join(
            #     [i.content for i in state["messages"]])
            # summary = self.llm.invoke(summary_prompt)
            # state["user_info"] = summary
            # state["messages"].append(f"Memory Updated: {summary}")
            # logger.debug(summary)
            return state

        self.graph.add_node("rag_search", rag_search)
        self.graph.add_node("tone_rewrite", tone_rewrite_node)
        self.graph.add_node("update_memory", update_memory_node)

        self.graph.add_edge(START, "rag_search")
        self.graph.add_edge("rag_search", "tone_rewrite")
        self.graph.add_edge("tone_rewrite", END)
        self.graph.add_edge("tone_rewrite", "update_memory")

    @log_execution_time(logger)
    def run(self, patient_input: str, user_id: str, user_info: str = None) -> Iterator[dict[str, Any] | Any]:
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
            {"messages": init_input, "user_info": user_info, "user_id": user_id}, config=config, stream_mode="updates"
        )
        final_outputs = [
            item["tone_rewrite"]["messages"][-1]
            for item in output
            if "tone_rewrite" in item
        ]
        # 如果只需要第一个：
        final_output = final_outputs[0] if final_outputs else None
        logger.debug(final_output)
        return final_output


class ReportAgentGraph:
    def __init__(self, use_short_term_memory: bool = True, use_long_term_memory: bool = False):
        self.llm = get_llm()
        self.use_short_term_memory = use_short_term_memory
        self.use_long_term_memory = use_long_term_memory
        self.short_term_memory = ShortTermMemory() if use_short_term_memory else None
        self.long_term_memory = LongTermMemory() if use_long_term_memory else None

        self.graph = StateGraph(State)

        @log_execution_time(logger)
        def rag_search(state: State) -> State:
            query_input = state["messages"][0].content
            report_kb = MilvusVectorKnowledgeBase(collection_name="report_knowledge")
            rag_result = vector_knowledge_query(query_input, report_kb)
            prompt = get_prompt_template("report_generation").format(patient_input=query_input,
                                                                     user_info=state["user_info"],
                                                                     rag_result=rag_result)
            llm_response = self.llm.invoke(prompt)
            state["messages"].append(f"LLM Report Response: {llm_response}")
            logger.debug(llm_response)
            return state

        @log_execution_time(logger)
        def tone_rewrite_node(state: State) -> State:
            last_response = state["messages"][-1].content
            tone_kb = MilvusVectorKnowledgeBase(collection_name="report_tone_kb")
            rag_result = vector_knowledge_query(last_response, tone_kb)
            prompt = get_prompt_template("tone_rewrite").format(result=last_response, rag_result=rag_result)
            llm_response = self.llm.invoke(prompt)
            state["messages"].append(str(llm_response))
            logger.debug(llm_response)
            return state

        @log_execution_time(logger)
        def update_memory_node(state: State) -> State:
            if self.use_short_term_memory:
                self.short_term_memory.add(state["user_id"], state["messages"])
            if self.use_long_term_memory:
                self.long_term_memory.add(state["user_id"], state["messages"])

            summary_prompt = "请总结以下报告中的重要内容，用于更新用户健康信息：\n" + \
                             "\n".join([m.content for m in state["messages"]])
            summary = self.llm.invoke(summary_prompt)
            state["user_info"] += summary
            state["messages"].append(f"Memory Updated: {summary}")
            logger.debug(summary)
            return state

        self.graph.add_node("rag_search", rag_search)
        self.graph.add_node("tone_rewrite", tone_rewrite_node)
        self.graph.add_node("update_memory", update_memory_node)

        self.graph.add_edge(START, "rag_search")
        self.graph.add_edge("rag_search", "tone_rewrite")
        self.graph.add_edge("tone_rewrite", "update_memory")
        self.graph.add_edge("tone_rewrite", END)

    @log_execution_time(logger)
    def run(self, patient_input: str, user_id: str, user_info: str = None) -> Iterator[dict[str, Any] | Any]:
        prompt_template = f"Patient Input: {patient_input}"
        context = ""
        if self.use_short_term_memory:
            context = self.short_term_memory.get_context(user_id)
        init_input = f"{context}\n{prompt_template}"
        chain = self.graph.compile()
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        output = chain.invoke(
            {"messages": init_input, "user_info": user_info, "user_id": user_id}, config=config, stream_mode="updates"
        )
        final_output = output["tone_rewrite"]["messages"][-1]
        logger.debug(final_output)
        return final_output

if __name__ == "__main__":
    print("=== 诊断 Agent 示例 ===")
    diag_agent = DiagnosisAgentGraph()
    diag_response = diag_agent.run("我最近连续几天发热并伴有头痛，感到非常焦虑。", '0')
    print("诊断回复：")
    print(diag_response)

    print("\n=== 报告解析 Agent 示例 ===")
    report_agent = ReportAgentGraph()
    report_response = report_agent.run("体检报告显示血脂异常、血糖偏高。")
    print("报告解析回复：")
    print(report_response)
