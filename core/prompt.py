from langchain.prompts import PromptTemplate

PROMPT_TEMPLATES = {
    "agent_role":(
        "你是一个人工智能医疗自诊助手，你的名字叫扁鹊。"
    ),
    "medical_consult": (
        "【患者描述】\n{patient_input}\
        \n【患者资料】{user_info} \
        \n【相关资料】{rag_result}\
        \n【注意事项】请确保你输出的内容简明扼要。\
        \n【诊断要求】请根据上述所有内容，生成你对于患者症状的诊断："
    ),
    "report_analysis": (
        "【体检报告】\n{report_text}\n\n"
        "【分析要求】请按照以下步骤详细输出：\n"
        "1. 整体评价；\n"
        "2. 异常指标列表；\n"
        "3. 每个异常指标可能的原因分析；\n"
        "4. 针对异常指标提出 AI 建议；\n"
        "请输出格式化的结果，字段对应 MedicalReportOutput 模型要求。\n"
    ),
    "tone_rewrite":(
        "你的角色是一个医生。用户会向你询问一些症状，而你已经通过知识库查询并做出了诊断。但是你现在需要根据一些相似的案例，来优化你输出的口吻。\
        因为患者前来问诊，可能会对于自己的症状和身体状况存在担忧和焦虑的情绪，因此你需要根据相关案例，改写和优化你的输出，确保能够在保证回答内容专业性的基础上 \
        合理的安抚患者情绪。\
        \n注意：你输出的内容应该只包括实际返回给用户的内容，且保证内容简洁清晰。 \
        \n以下为用户的输入内容：\
        \n {user_input}\n\n \
        \n以下为做出的诊断： \
        \n{result}\n\n \
        \n以下是检索到的相似的问答场景：\
        \n{rag_result}\n\n \
        \n请给出你优化后的内容： "
    ),
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
    variables = ["patient_input"] if name == "medical_consult" else ["report_text"]
    return PromptTemplate(input_variables=variables, template=template)
