from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
import custLLma
import panel as pn
import param
import os
import logging
import envInit
import datetime
import traceback
import dealFile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TTL = 1800  # 30 minutes
pn.extension("perspective")
instenv = envInit.localbot()
chat_history = []

class State(param.Parameterized):
    instenv = envInit.localbot()
    target_folder = instenv.VECTOR_DB_PATH
    model_name: str = instenv.LLM_LOCAL_MODEL
    upload_file: bytes = param.Bytes()
    embeddingsmodel_name: str = instenv.EMBEDDING_MODEL_PATH + '/' + instenv.EMBEDDING_MODEL

def get_vectordbs():
    target_folder = instenv.VECTOR_DB_PATH
    vectordbs = []
    for item in os.listdir(target_folder):
        if os.path.isdir(os.path.join(target_folder, item)):
            vectordbs.append(item)
    return vectordbs

def ref_dbs():
    # 查找目录下的文件夹名称
    target_folder = instenv.VECTOR_DB_PATH
    vectordbs = []
    for item in os.listdir(target_folder):
        if os.path.isdir(os.path.join(target_folder, item)):
            vectordbs.append(item)
    chain_type: str = param.Selector(
        objects=vectordbs
    )
    return chain_type

def get_retriever(embeddingsmodel_name, faiss_path):
    try:
        print('faiss_path', faiss_path)
        embedding = HuggingFaceEmbeddings(model_name=embeddingsmodel_name,
                                          model_kwargs={'device': 'cpu'})
        vectordb = FAISS.load_local(faiss_path, embedding, allow_dangerous_deserialization=True)
        return vectordb.as_retriever()
    except Exception as e:
        traceback.print_exc()
        print("An error occurred while loading the retriever:", str(e))
        return None
def _save_file(contents, instance: pn.chat.ChatInterface):
    file_input = instance.widgets[1]
    if file_input.value is None:
        return "E: No file selected."
    # Get the filename and file extension
    file_name = file_input.filename
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
    print(" _save_file :", str(file_path))
    # Save file
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
    try:
        dealFile.import_file_to_vectorsdb(file_path)
        new_file_name = os.path.splitext(os.path.basename(new_file_name))[0]
        # Define the directory to save files
        directory = instenv.VECTOR_DB_PATH + '/' + new_file_name
        if not os.path.exists(directory):
            os.makedirs(directory)

        print(" 文件上传成功，生成向量数据库成功！ :", str(new_file_name))
        return "文件上传成功，生成向量数据库成功！"
    except:
        return "上传文件失败，请重新上传！"

def _get_retrieval_qa(chain_type: str):
    model_name = instenv.LLM_LOCAL_MODEL
    embeddingsmodel_name: str = instenv.EMBEDDING_MODEL_PATH + '/' + instenv.EMBEDDING_MODEL
    faiss_path = instenv.VECTOR_DB_PATH + '/' + chain_type
    llm = custLLma.CustomLLM(model_name=model_name)
    retriever = get_retriever(embeddingsmodel_name, faiss_path)
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        verbose=True,
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
    )
    return qa

def get_retriever(embeddingsmodel_name, faiss_path):
    try:
        print('faiss_path', faiss_path)
        embedding = HuggingFaceEmbeddings(model_name=embeddingsmodel_name,
                                          model_kwargs={'device': 'cpu'})
        vectordb = FAISS.load_local(faiss_path, embedding, allow_dangerous_deserialization=True)
        return vectordb.as_retriever()
    except Exception as e:
        traceback.print_exc()
        print("An error occurred while loading the retriever:", str(e))
        return None

def _get_retrieval_qa(vertor_db):
    model_name = instenv.LLM_LOCAL_MODEL
    embeddingsmodel_name: str = instenv.EMBEDDING_MODEL_PATH + '/' + instenv.EMBEDDING_MODEL
    faiss_path = instenv.VECTOR_DB_PATH + '/' + str(vertor_db)
    llm = custLLma.CustomLLM(model_name=model_name)
    retriever = get_retriever(embeddingsmodel_name, faiss_path)
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        verbose=True,
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
    )
    return qa

def vertor_chat(vertor_db,question,chat_history):
    try:
        qa = _get_retrieval_qa(vertor_db)
        response = qa.invoke({"question": question, "chat_history": chat_history})
        return "S", response["answer"]
    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        return "E", error_message

def robot_chat(question):
    try:
        model_name = instenv.LLM_LOCAL_MODEL
        llm = custLLma.CustomLLM(model_name=model_name)
        response = llm.invoke(question)
        return "S", response
    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        return "E", error_message
