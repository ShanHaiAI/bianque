# front/web_ui.py
import gradio as gr

from front.ocr import process_image


# 添加报告处理函数
def analyze_report(image):
    if image is None:
        return "请先上传报告图片"

    try:
        # 调用OCR处理图片并获取文本列表
        text_list = process_image(image.name)  # 返回文本列表
        # 将文本列表转换为字符串
        result = '\n'.join(text_list) if isinstance(text_list, list) else str(text_list)
        return f"报告解析结果：\n{result}"
    except Exception as e:
        return f"解析失败：{str(e)}"


def close_dialog():
    return gr.update(visible=False)


def call_large_model(input_text):
    # 这里模拟调用大模型的过程
    # 实际实现中，这里可能是调用 API 或本地模型
    response = f"模型响应：{input_text} 已处理"
    return response


def process_input(input_text, chat_history):
    # 调用大模型
    response = call_large_model(input_text)
    # 将用户输入和模型响应添加到聊天历史中

    chat_history.append({"role": "user", "content": input_text})
    chat_history.append({"role": "assistant", "content": response})
    return chat_history


def submit_info(gender):
    # 根据性别选择头像
    if gender == "女":
        avatar = './static/woman.jpg'
    else:
        avatar = './static/man.jpg'
    return gr.update(visible=False), gr.update(avatar_images=(avatar, './static/doctor.jpg'))


with (gr.Blocks(css_paths='./static/theme.css', theme=gr.themes.Default()) as demo):
    with gr.Row():
        gr.Image(value='./static/banner.jpg',
                 elem_id="bianque-image",
                 show_fullscreen_button=False,
                 show_download_button=False,
                 container=False,
                 )

    chatbot = gr.Chatbot(label="扁鹊对话",
                         elem_id="chatbot",
                         type="messages",
                         show_label=False,
                         container=False,
                         value=[{"role": "assistant",
                                 "content": "你好，我是扁鹊，你的AI自诊助理。如果有什么身体不舒服的地方，可以告诉我，我会给你一些健康相关的建议。"}],
                         sanitize_html=False,
                         avatar_images=('./static/man.jpg', './static/doctor.jpg'),
                         )

    # 创建一个悬浮窗（对话框）
    with gr.Column(visible=False, elem_classes="dialog") as dialog:
        with gr.Row(elem_id="dialog-header"):
            with gr.Column(scale=3):
                gr.Markdown("### 录入信息", elem_id="dialog-title")
            with gr.Column(scale=1,min_width=0):
                close_btn = gr.Button("×", elem_id="close-btn",min_width=0)
        close_btn.click(fn=close_dialog, inputs=[], outputs=dialog)
        age = gr.Number(label="年龄")
        gender = gr.Radio(label="性别", choices=["男", "女"])
        medical_record = gr.Textbox(label="即往病史", submit_btn=False, lines=5, )
        submit_btn = gr.Button("提交", elem_classes="block-submit",min_width=0)
        submit_btn.click(fn=submit_info, inputs=gender, outputs=[dialog, chatbot])
    button = gr.Button(
        value="",
        icon='./static/user-circle.svg'
        , elem_id="person-btn")
    button.click(fn=lambda: gr.update(visible=True),
                 inputs=[],
                 outputs=dialog)

    with gr.Column(elem_id="content-container"):  # 包裹主要内容，控制宽度
        with gr.Tabs():
            with gr.TabItem("问问扁鹊"):
                # 文字输入框

                text_input = gr.Textbox(placeholder="请输入您的症状描述",
                                        submit_btn='➤',
                                        # show_label=True,
                                        # interactive=True,
                                        container=False,
                                        lines=5,
                                        elem_classes="tab-input"
                                        )

                text_input.submit(fn=process_input, inputs=[text_input, chatbot], outputs=[chatbot])
                text_input.submit(lambda: "", inputs=[], outputs=text_input)
            with gr.TabItem("看看报告"):
                image_input = gr.File(
                    height=115,
                    show_label=False,
                    elem_classes="tab-input"
                )
                gr.Button('➤',
                          elem_id="analysis-btn",
                          elem_classes="block-submit")
    gr.Markdown("温馨提示：所有建议仅供参考，如有异常请及时就医。", elem_id="markdown-text")

demo.launch(
    debug=True)
