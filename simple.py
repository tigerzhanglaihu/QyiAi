import qyiutil
import panel as pn
import custLLma

# 初始化机器人状态和聊天历史
state = qyiutil.State()
chat_history = []
# 定义输入文本框
text_input = pn.widgets.TextInput(placeholder="输入你想提问的问题！")

# 定义获取机器人回应的函数
def _get_response(contents):
    # 加载并初始化 LLma 模型
    model_name = "chatglm3-6b"
    llm = custLLma.CustomLLM(model_name=model_name)
    # 调用模型生成回应
    response = llm.invoke(contents)
    # 将问题和回应添加到聊天历史中
    chat_history.extend([(contents, response)])
    return response

# 定义响应用户输入的函数
async def respond(contents, user, chat_interface):
    # 获取机器人的回应
    response = _get_response(contents)
    '''
     avatar (str | BinaryIO): The avatar to use for the user.
     Can be a single character text, an emoji, or anything supported by pn.pane.Image. 
     If not set, uses the first character of the name.
     default_avatars (Dict[str, str | BinaryIO]): A default mapping of user names to their corresponding avatars to use when the user is set but the avatar is not. 
     You can modify, but not replace the dictionary.
     Note, the keys are only alphanumeric sensitive, meaning spaces, special characters, and case sensitivity is disregarded, e.g. "Chat-GPT3.5", "chatgpt 3.5" and "Chat GPT 3.5" all map to the same value.
     '''
    # 返回回应给用户
    yield {"user": "Qyi", "avatar":"🤖️" , "object": response}
# 创建聊天界面
chat_interface = pn.chat.ChatInterface(
    widgets=[text_input],
    callback=respond,
    callback_exception='verbose',
    sizing_mode="stretch_width",
    renderers=pn.pane.Perspective,
    show_rerun=False,
    show_undo=False,
    show_clear=False,
)
# 发送欢迎消息
chat_interface.send(
    "QyiAI-本地知识库极简版本",
    user="system",
    respond=False
)
# 获取当前模型的描述
model_desc = '模型：' + state.model_name

# 创建 Bootstrap 模板
template = pn.template.BootstrapTemplate(
    title="QyiAI-本地知识库极简版本",
    sidebar=[
        model_desc,
    ],
    main=[chat_interface],
)

# 显示模板
template.servable()
template.show()
