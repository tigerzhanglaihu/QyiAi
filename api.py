#  ===================================================
#  -*- coding:utf-8 -*-
#  ===================================================
#  Copyright (C) Global Enterprise Solutions Co.,Ltd.
#             AllRights Re10served
#  ===================================================
#  ===================================================
#  Program Name:
#       QyiAI 支持的 api
#  Description:
#       Api 的清单
#  History:
#      1.00  2024.04.03  zhanglaihu  Creation
#      2.00  2024.04.14  zhanglaihu  update
# ==================================================*/
import os
import dealFile
import qyiutil
import datetime
import envInit
import logging
import shutil
#import panel as pn
from fastapi import FastAPI, UploadFile
import uvicorn

app = FastAPI()

# 假设的用于处理文件上传和存储的函数
def handle_uploaded_file(upload_file):
    try:
        instenv = envInit.localbot()
        # Get the filename and file extension
        file_name = upload_file.filename
        file_extension = file_name.split(".")[-1]
        # Generate file name with current datetime
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if len(file_name) <= 10:
            new_file_name = f"{file_name.split('.')[0]}_{current_time}.{file_extension}"
        else:
            new_file_name = f"UserFile_{current_time}.{file_extension}"
        # Define the directory to save files
        directory = instenv.FILE_UPLOAD_PATH
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, new_file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        return_status = 'S'
        return_message = " _save_file :" + str(file_path)
    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        return_status = 'E'
        return_message = str(e)
    # 使用jsonify创建一个JSON响应
    response =  {"return_status": return_status, "return_message": return_message}
    return response
#假设的用于生成向量数据库的函数
def generate_vector_db(file_path):
    # 在这里实现生成向量数据库的逻辑
    return_status, return_message = dealFile.import_file_to_vectorsdb(file_path)
    # 使用jsonify创建一个JSON响应
    response = {"return_status": return_status, "return_message": return_message}
    return response

# 假设的用于聊天的函数
def chat_with_vector_db(vector_db_path, question):
    # 在这里实现与向量数据库进行聊天的逻辑
    # 例如，加载向量数据库，根据问题生成回答
    # ... 加载数据库和生成回答 ...
    return_status, return_message = qyiutil.vertor_chat(vector_db_path, question, [])
    # 使用jsonify创建一个JSON响应
    response = {"return_status": return_status, "return_message": return_message}
    return response

def llmchat(question):
    return_status, return_message = qyiutil.robot_chat(question)
    # 使用jsonify创建一个JSON响应
    response = {"return_status": return_status, "return_message": return_message}
    return response


@app.post('/api/uploadfile')
async def upload_file(file: UploadFile ):
    upload_file = file
    return_json = handle_uploaded_file(upload_file)
    return return_json

@app.post('/api/gen_vector_db')
async def gen_vector_db(file_path:str):
    return_json = generate_vector_db(file_path)
    return return_json


@app.post('/api/chat')
async def chat(vector_db_path : str, question:str):
    return_json = chat_with_vector_db(vector_db_path, question)
    return return_json


@app.post('/api/llmchat')
async def chat(question:str):
    return_json = llmchat(question)
    return return_json

#uvicorn api:app --reload
uvicorn.run(app, host="localhost", port=8000)
