#  ===================================================
#  -*- coding:utf-8 -*-
#  ===================================================
#  Copyright (C) Global Enterprise Solutions Co.,Ltd.
#             AllRights Re10served
#  ===================================================
#  ===================================================
#  Program Name:
#       QyiAI 基于本地文档的知识库
#  Description:
#       主要支持pdf，word，txt文件内容
#  History:
#      1.00  2024.04.03  zhanglaihu  Creation
#      2.00  2024.04.14  zhanglaihu  update
# ==================================================*/
import qyiutil
import panel as pn
#初始化
state = qyiutil.State()
# Define the widgets
text_input = pn.widgets.TextInput(placeholder="选择一个你需要对话的数据库！")
file_input = pn.widgets.FileInput(name="上传文件", accept=".pdf,.csv,.txt")
chat_history = []
vectordbs_options = qyiutil.get_vectordbs()
# 创建向量数据库选择器
chain_type_input = pn.widgets.RadioButtonGroup(
    name="本地向量数据库名称",
    options= vectordbs_options,
    orientation="vertical",
    sizing_mode="stretch_width",
    button_type="primary",
    button_style="outline",
)
def _get_response(contents):
    qa = qyiutil._get_retrieval_qa(chain_type_input.value)
    response = qa.invoke({"question": contents, "chat_history": chat_history})
    chat_history.extend([(contents, response["answer"])])
    chunks = []
    return response, chunks
async def respond(contents, user, chat_interface):
    if chat_interface.active == 0:
        response, documents = _get_response(contents)
        yield {"user": "Qyi", "avatar": "🤖️","object": response["answer"]}

    if chat_interface.active == 1:
        chat_interface.active = 0
        yield {"user": "Qyi", "avatar": "🤖️", "object": "文件正在处理中，请稍后...."}
        upload_message = qyiutil._save_file(contents, chat_interface)
        #获取新的
        chain_type_input.options = qyiutil.get_vectordbs()
        yield {"user": "Qyi", "avatar": "🤖️", "object": "文件上传完成," + str(upload_message) }

chat_interface = pn.chat.ChatInterface(
    widgets=[text_input, file_input],
    callback=respond,
    callback_exception='verbose',
    sizing_mode="stretch_width",
    renderers=pn.pane.Perspective,
    show_rerun=False,
    show_undo=False,
    show_clear=False,
)
# 欢迎
chat_interface.send(
    "QyiAI - 基于本地知识库机器人",
    user="system",
    respond=False
)
model_desc = '模型：' + state.model_name
template = pn.template.BootstrapTemplate(
    title="QyiAI - 基于本地知识库机器人",
    sidebar=[
        model_desc,
        "本地向量数据库名称",
        chain_type_input,
    ],
    main=[chat_interface],
)
# 将按钮添加到主界面中
template.servable()
template.show()
