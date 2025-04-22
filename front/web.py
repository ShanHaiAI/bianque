import uuid

import gradio as gr

from front.ocr import process_image
from core import diag_agent, report_agent

shortcut_js = """
<script>
function shortcuts(e) {
    if (e.key.toLowerCase() == "enter" && e.ctrlKey) {
        document.getElementById("analysis-btn").click();
    }
}
document.addEventListener('keypress', shortcuts, false);
</script>
"""


# 添加报告处理函数
def analyze_report(image):
    if image is None:
        return "请先上传报告图片"

    try:
        # 调用OCR处理图片并获取文本列表
        text_list = process_image(image.name)  # 返回文本列表
        # 将文本列表转换为字符串
        return '\n'.join(text_list) if isinstance(text_list, list) else str(text_list)
    except Exception as e:
        return f"解析失败：{str(e)}"


def close_dialog():
    return gr.update(visible=False)


def call_large_model(input_text, user_conf):
    response_iterator = diag_agent.run(input_text, user_id=user_conf['user_id'], user_info=user_conf['user_info'])
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


def call_report_model(input_text, user_conf):
    response_iterator = report_agent.run(input_text, user_id=user_conf['user_id'], user_info=user_conf['user_info'])

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

def add_content(input_text, image_input, chat_history, user_conf):
    if not user_conf.get('user_id'):
        user_conf['user_id'] = str(uuid.uuid4())
    # 检查输入是否为空
    if user_conf['select_tab'] == 1:
        if not input_text or input_text.isspace():
            gr.Warning("请输入问题")
            return input_text, image_input, chat_history, user_conf
        else:
            # 添加用户消息
            chat_history.append({"role": "user", "content": input_text})
            # 获取助手回复
    else:
        if not image_input:
            gr.Warning("请先上传图片")
            return input_text, image_input, chat_history, user_conf
        else:
            # 添加用户消息
            chat_history.append({"role": "user", "content": gr.File(image_input)})
    return chat_history, user_conf


def process_input(input_text, image_input, chat_history, user_conf):
    if not user_conf.get('user_id'):
        user_conf['user_id'] = str(uuid.uuid4())
    # 检查输入是否为空
    bot_response = ""
    if user_conf['select_tab'] == 1:
        if not input_text or input_text.isspace():
            gr.Warning("请输入问题")
            return input_text, image_input, chat_history, user_conf
        else:
            # 添加用户消息
            chat_history.append({"role": "user", "content": input_text})
            # 获取助手回复
            try:
                for chunk in call_large_model(input_text, user_conf):
                    bot_response += str(chunk)
            except Exception as e:
                bot_response = f"发生错误: {str(e)}"
            # 添加助手消息
    else:
        if not image_input:
            gr.Warning("请先上传图片")
            return input_text, image_input, chat_history, user_conf
        else:
            ocr_resp = analyze_report(image_input)
            # 添加用户消息
            chat_history.append({"role": "user", "content": gr.File(image_input)})
            # 获取助手回复
            bot_response = ""
            try:
                for chunk in call_report_model(ocr_resp, user_conf):
                    bot_response += str(chunk)
            except Exception as e:
                bot_response = f"发生错误: {str(e)}"
    chat_history.append({"role": "assistant", "content": bot_response})
    return "", None, chat_history, user_conf


def call_large_model_stream(input_text, user_info):
    """
    流式调用大模型诊断 Agent，逐段返回响应内容
    """
    try:
        response_iterator = diag_agent.run(input_text, user_id='0', user_info=user_info)
        for chunk in response_iterator:
            if isinstance(chunk, dict):
                message = chunk.get('content', '') or chunk.get('message', '')
                if message:
                    yield message
            else:
                yield str(chunk)
    except Exception as e:
        yield f"发生错误: {str(e)}"


def process_input_stream(input_text, chat_history, user_info):
    """
    处理用户输入并流式返回助手响应，适用于 Gradio ChatInterface 的 generator 模式
    """
    if not input_text or input_text.isspace():
        yield "", chat_history
        return

    # 添加用户消息
    chat_history.append({"role": "user", "content": input_text})
    bot_message = ""

    try:
        for chunk in call_large_model_stream(input_text, user_info):
            bot_message += chunk
            # 实时 yield 中间结果（每次更新 bot 说的内容）
            yield "", chat_history + [{"role": "assistant", "content": bot_message}]
    except Exception as e:
        bot_message = f"发生错误: {str(e)}"
        yield "", chat_history + [{"role": "assistant", "content": bot_message}]


# 定义更新函数
def select_diag(user_conf):
    user_conf['select_tab'] =  1  # 更新 select_tab 字段
    return user_conf  # 返回更新后的 user_conf

def select_report(user_conf):
    user_conf['select_tab'] =  2  # 更新 select_tab 字段
    return user_conf  # 返回更新后的 user_conf



def submit_info(age, gender, medical_record,user_session):
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
    user_session['user_info'] = pd.DataFrame(user_info)
    return gr.update(visible=False), gr.update(avatar_images=(avatar, './static/doctor.jpg')), user_session


with (gr.Blocks(css_paths='./static/theme.css', head=shortcut_js, theme=gr.themes.Default()) as demo):
    with gr.Row():
        gr.Image(value='./static/banner.jpg',
                 elem_id="bianque-image",
                 show_fullscreen_button=False,
                 show_download_button=False,
                 container=False,
                 )
    user_session = gr.State(value={'select_tab': 1,
                                'user_id': None,
                                'user_info': None
                                   })
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
        submit_btn.click(fn=submit_info, inputs=[age, gender, medical_record,user_session],
                         outputs=[dialog, chatbot, user_session])
    button = gr.Button(
        value="",
        icon='./static/user-circle.svg'
        , elem_id="person-btn")
    button.click(fn=lambda: gr.update(visible=True),
                 inputs=[],
                 outputs=dialog)

    with gr.Column(elem_id="content-container"):  # 包裹主要内容，控制宽度
        with gr.Tabs() as tabs:
            with gr.TabItem("问问扁鹊") as diag_tab:
                # 文字输入框
                diag_tab.select(fn=select_diag, inputs=[user_session], outputs=[user_session])
                text_input = gr.Textbox(placeholder="请输入您的症状描述（按Ctrl+Enter发送）",
                                        # interactive=True,
                                        container=False,
                                        lines=5,
                                        elem_classes="tab-input",
                                        elem_id="submit-textbox-btn",
                                        )
            with gr.TabItem("看看报告") as report_tab:
                report_tab.select(fn=select_report, inputs=[user_session], outputs=[user_session])
                image_input = gr.File(
                    show_label=False,
                    elem_classes="tab-input"
                )
            submit = gr.Button('➤',
                               elem_id="analysis-btn",
                               elem_classes="block-submit")
            submit.click(fn=add_content,
                         inputs=[text_input, image_input, chatbot, user_session],
                         outputs=[chatbot, user_session])
            submit.click(fn=process_input,
                         inputs=[text_input, image_input, chatbot, user_session],
                         outputs=[text_input, image_input, chatbot, user_session])
    gr.Markdown("温馨提示：所有建议仅供参考，如有异常请及时就医。", elem_id="markdown-text")
