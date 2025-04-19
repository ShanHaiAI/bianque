# front/web_ui.py
import gradio as gr


def close_dialog():
    return gr.update(visible=False)


def submit_info(name, age, gender):
    return f"提交的信息：\n姓名: {name}\n年龄: {age}\n性别: {gender}"


with gr.Blocks(css_paths='./static/theme.css', theme=gr.themes.Default()) as demo:
    # 创建一个悬浮窗（对话框）
    with gr.Column(visible=False, elem_classes="dialog") as dialog:
        close_btn = gr.Button("×", elem_id="close-btn")
        close_btn.click(fn=close_dialog, inputs=[], outputs=dialog)
        age = gr.Number(label="年龄")
        gender = gr.Radio(label="性别", choices=["男", "女"])
        medical_record = gr.Textbox(label="即往病史", submit_btn=False, lines=5, )
        submit_btn = gr.Button("提交", elem_classes="block-submit")
    button = gr.Button(
        value="",
        icon='./static/user-circle.svg'
        , elem_id="person-btn")
    button.click(fn=lambda: gr.update(visible=True),
                 inputs=[],
                 outputs=dialog)
    with gr.Row():
        gr.Image(value='./static/banner.jpg',
                 elem_id="bianque-image",
                 show_fullscreen_button=False,
                 show_download_button=False,
                 container=False,
                 )

    with gr.Column(elem_id="content-container"):  # 包裹主要内容，控制宽度
        with gr.Tabs():
            with gr.TabItem("问问扁鹊"):
                # 文字输入框
                with gr.Column(elem_id="input-dialog"):
                    text_input = gr.Textbox(placeholder="请输入您的症状描述",
                                            submit_btn='➤',
                                            # show_label=True,
                                            # interactive=True,
                                            container=False,
                                            lines=5,
                                            elem_id="text-input")
                    # 文件上传和语音输入按钮
                    # submit_btn = gr.Button("问问扁鹊", elem_id="submit-btn")
            with gr.TabItem("看看报告"):
                image_input = gr.File(show_label=False, elem_id="image-input")
                gr.Button("解析报告", elem_classes="block-submit")
        gr.Markdown("温馨提示：所有建议仅供参考，如有异常请及时就医。", elem_id="markdown-text")

demo.launch(
    debug=True)
