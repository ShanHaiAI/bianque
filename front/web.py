# front/web_ui.py
import gradio as gr

from front.ocr import process_image
from core import diag_agent


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


def call_large_model(input_text,user_info):
    response_iterator = diag_agent.run(input_text, user_id='0',user_info=user_info)
    full_response = ""

    try:
        for chunk in response_iterator:
            if isinstance(chunk, dict):
                message = chunk.get('content', '') or chunk.get('message', '')
                full_response += message
            else:
                full_response += str(chunk)
        return full_response
    except Exception as e:
        return f"发生错误: {str(e)}"

def process_input(input_text, chat_history,user_info):

    # 检查输入是否为空
    if not input_text or input_text.isspace():
        return "", chat_history  # 返回空字符串，保持聊天历史不变
    # 添加用户消息
    chat_history.append({"role": "user", "content": input_text})

    # 获取助手回复
    bot_response = ""
    try:
        for chunk in call_large_model(input_text,user_info):
            bot_response += str(chunk)
    except Exception as e:
        bot_response = f"发生错误: {str(e)}"

    # 添加助手消息
    chat_history.append({"role": "assistant", "content": bot_response})
    return "", chat_history


def submit_info(age, gender, medical_record):
    # 创建用户信息字典
    user_info = {
        'age': [age],
        'gender': [gender],
        'medical_history': [medical_record]
    }

    # 转换为DataFrame
    import pandas as pd

    # 根据性别选择头像
    avatar = './static/woman.jpg' if gender == "女" else './static/man.jpg'


    return gr.update(visible=False), gr.update(avatar_images=(avatar, './static/doctor.jpg')),pd.DataFrame(user_info)



with (gr.Blocks(css_paths='./static/theme.css', theme=gr.themes.Default()) as demo):
    with gr.Row():
        gr.Image(value='./static/banner.jpg',
                 elem_id="bianque-image",
                 show_fullscreen_button=False,
                 show_download_button=False,
                 container=False,
                 )
    user_info_state = gr.State(value=None)
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
            with gr.Column(scale=1, min_width=0):
                close_btn = gr.Button("×", elem_id="close-btn", min_width=0)
        close_btn.click(fn=close_dialog, inputs=[], outputs=dialog)
        age = gr.Number(label="年龄")
        gender = gr.Radio(label="性别", choices=["男", "女"])
        medical_record = gr.Textbox(label="即往病史", submit_btn=False, lines=5, )
        submit_btn = gr.Button("提交", elem_classes="block-submit", min_width=0)
        submit_btn.click(fn=submit_info, inputs=[age, gender, medical_record], outputs=[dialog, chatbot,user_info_state])
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

                text_input = gr.Textbox(placeholder="请输入您的症状描述（按Enter发送）",
                                        submit_btn='➤',
                                        # show_label=True,
                                        # interactive=True,
                                        container=False,
                                        lines=5,
                                        elem_classes="tab-input"
                                        )
                text_input.js = """
                    function(e) {
                        if (e.ctrlKey && e.key === 'Enter') {
                            document.querySelector('#submit-btn').click();
                            return;
                        }
                    }
                    """
                # 在submit事件中启用队列
                text_input.submit(fn=process_input,
                                  inputs=[text_input, chatbot,user_info_state],
                                  outputs=[text_input, chatbot])  # 启用队列支持
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