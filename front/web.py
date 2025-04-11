# front/web_ui.py
import gradio as gr
from core.diagnosis_agent import DiagnosisAgent
from core.report_agent import ReportAgent
from ocr_tool import ocr_extract_text
from rag_tool import MilvusVectorKnowledgeBase


def consult(patient_input):
    agent = DiagnosisAgent()
    return agent.run(patient_input)


def analyze_report(report_text):
    agent = ReportAgent()
    return agent.run(report_text)


def ocr_demo(image):
    temp_path = "temp_report.jpg"
    image.save(temp_path)
    text = ocr_extract_text(temp_path)
    return text


def upload_documents(files):
    texts = []
    for file_obj in files:
        text = file_obj.read().decode("utf-8")
        texts.append(text)
    kb = MilvusVectorKnowledgeBase()
    result = kb.insert_documents(texts)
    return result


with gr.Blocks() as demo:
    gr.Markdown("## 扁鹊 AI 医疗自诊")

    with gr.Tabs():
        with gr.TabItem("在线问诊"):
            text_input = gr.Textbox(lines=5, label="请输入您的症状描述")
            output_text = gr.Textbox(lines=10, label="问诊结果")
            gr.Button("提交问诊").click(fn=consult, inputs=text_input, outputs=output_text)

        with gr.TabItem("体检报告解析"):
            image_input = gr.Image(type="pil", label="上传体检报告图片")
            ocr_output = gr.Textbox(label="OCR 解析结果")
            gr.Button("解析报告").click(fn=ocr_demo, inputs=image_input, outputs=ocr_output)

        with gr.TabItem("知识库构建", visible=False):  # 隐藏页面：仅授权用户可访问
            gr.Markdown("### 上传专业文档构建向量知识库")
            file_upload = gr.File(file_count="multiple", label="上传文档（文本格式）")
            upload_output = gr.Textbox(label="上传结果")
            gr.Button("上传文档").click(fn=upload_documents, inputs=file_upload, outputs=upload_output)

    gr.Markdown("温馨提示：所有建议仅供参考，如有异常请及时就医。")

demo.launch()
