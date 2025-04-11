from langchain.prompts import PromptTemplate

PROMPT_TEMPLATES = {
    "medical_consult": (
        "【患者描述】\n{patient_input}\n\n"
        "【诊断要求】请根据上述患者描述，依次输出以下内容：\n"
        "1. 可能的症状及原因分析；\n"
        "2. MCP 数据查询的相关信息；\n"
        "3. RAG 检索得到的相关专业文档摘要；\n"
        "4. 最后以温馨、关怀的语气给出建议，并提醒该建议仅供参考，如有异常请及时就医。\n"
    ),
    "report_analysis": (
        "【体检报告】\n{report_text}\n\n"
        "【分析要求】请按照以下步骤详细输出：\n"
        "1. 整体评价；\n"
        "2. 异常指标列表；\n"
        "3. 每个异常指标可能的原因分析；\n"
        "4. 针对异常指标提出 AI 建议；\n"
        "请输出格式化的结果，字段对应 MedicalReportOutput 模型要求。\n"
    )
}


def get_prompt_template(name: str) -> PromptTemplate:
    """
    根据名称返回对应的 prompt 模板

    Args:
        name (str): 模板名称，如 "medical_consult" 或 "report_analysis"

    Returns:
        PromptTemplate: 格式化 prompt 模板
    """
    template = PROMPT_TEMPLATES.get(name)
    if not template:
        raise ValueError(f"未找到 {name} 对应的 prompt 模板")
    # 根据模板类型确定输入变量名称
    variables = ["patient_input"] if name == "medical_consult" else ["report_text"]
    return PromptTemplate(input_variables=variables, template=template)
