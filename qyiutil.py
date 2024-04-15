import os
import logging
import datetime
import traceback
import envInit
import custLLma
import panel as pn
import param
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
import dealFile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pn.extension("perspective")

# 初始化环境
instenv = envInit.localbot()


class State(param.Parameterized):
    instenv = envInit.localbot()
    target_folder = instenv.VECTOR_DB_PATH
    model_name = instenv.LLM_LOCAL_MODEL
    upload_file = param.Bytes()
    embeddingsmodel_name = instenv.EMBEDDING_MODEL_PATH + '/' + instenv.EMBEDDING_MODEL


# 获取向量数据库列表
def get_vectordbs():
    target_folder = instenv.VECTOR_DB_PATH
    return [item for item in os.listdir(target_folder) if os.path.isdir(os.path.join(target_folder, item))]


# 获取检索器
def get_retriever(embeddingsmodel_name, faiss_path):
    try:
        embedding = HuggingFaceEmbeddings(model_name=embeddingsmodel_name, model_kwargs={'device': 'cpu'})
        vectordb = FAISS.load_local(faiss_path, embedding, allow_dangerous_deserialization=True)
        return vectordb.as_retriever()
    except Exception as e:
        logging.error(f"An error occurred while loading the retriever: {str(e)}")
        return None


# 保存文件并生成向量数据库
def _save_file(contents, instance: pn.chat.ChatInterface):
    file_input = instance.widgets[1]
    if file_input.value is None:
        return "E: No file selected."

    file_name = file_input.filename
    file_extension = file_name.split(".")[-1]
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_file_name = f"{file_name.split('.')[0]}_{current_time}.{file_extension}" if len(
        file_name) <= 10 else f"UserFile_{current_time}.{file_extension}"
    directory = instenv.FILE_UPLOAD_PATH

    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, new_file_name)

    try:
        if file_extension == 'csv':
            file_contents = contents.to_csv(index=False).encode('utf-8')
            with open(file_path, 'wb') as f:
                f.write(file_contents)
        elif file_extension == 'pdf':
            file_contents = contents.getvalue()
            with open(file_path, 'wb') as f:
                f.write(file_contents)
        elif file_extension == 'txt':
            file_contents = contents
            with open(file_path, 'w') as f:
                f.write(file_contents)

        dealFile.import_file_to_vectorsdb(file_path)
        new_file_name = os.path.splitext(os.path.basename(new_file_name))[0]
        directory = instenv.VECTOR_DB_PATH + '/' + new_file_name
        if not os.path.exists(directory):
            os.makedirs(directory)

        return "文件上传成功，生成向量数据库成功！"
    except Exception as e:
        logging.error(f"An error occurred while saving the file: {str(e)}")
        return "上传文件失败，请重新上传！"


# 获取检索问题的 QA 对象
def _get_retrieval_qa(vertor_db):
    faiss_path = os.path.join(instenv.VECTOR_DB_PATH, str(vertor_db))
    llm = custLLma.CustomLLM(model_name=instenv.LLM_LOCAL_MODEL)
    retriever = get_retriever(instenv.EMBEDDING_MODEL_PATH + '/' + instenv.EMBEDDING_MODEL, faiss_path)
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        verbose=True,
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
    )
    return qa


# 向量数据库聊天
def vertor_chat(vertor_db, question, chat_history):
    try:
        qa = _get_retrieval_qa(vertor_db)
        response = qa.invoke({"question": question, "chat_history": chat_history})
        return "S", response["answer"]
    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        return "E", error_message


# 语言模型聊天
def robot_chat(question):
    try:
        llm = custLLma.CustomLLM(model_name=instenv.LLM_LOCAL_MODEL)
        response = llm.invoke(question)
        return "S", response
    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        return "E", error_message
