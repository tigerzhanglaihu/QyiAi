#  ===================================================
#  -*- coding:utf-8 -*-
#  ===================================================
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
import os
import shutil
import envInit
# Configure logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_csv_txt(file_path):
    # Load documents from CSV file
    loader = CSVLoader(file_path=file_path, encoding='utf8')
    docs = loader.load()
    return docs

def get_txtfile_txt(file_path):
    # Load documents from CSV file
    loader = TextLoader(file_path=file_path, encoding='utf8')
    docs = loader.load()
    return docs

def get_pdf_txt(file_path):
    # Load documents from CSV file
    loader = PyPDFLoader(file_path=file_path)
    docs = loader.load()
    return docs

def get_filename_without_extension(file_path):
    filename = os.path.basename(file_path)  # 获取文件名
    filename_without_extension = os.path.splitext(filename)[0]  # 去掉后缀
    return filename_without_extension


def faiss_db(directory):
    # 检查指定目录是否存在
    if not os.path.isdir(directory):
        print(f"The specified directory {directory} does not exist.")
        return False
    # 定义要检查的文件名
    file_names = ['index.faiss', 'index.pkl']
    # 检查所有文件是否都存在
    all_files_exist = all(os.path.isfile(os.path.join(directory, file_name)) for file_name in file_names)

    return all_files_exist


# Function to import files into vectorsdb
def import_file_to_vectorsdb(file_path):

    try:
        env = envInit.localbot()
        model_name = env.EMBEDDING_MODEL_PATH + '/' + env.EMBEDDING_MODEL

        # Log info function
        def log_info(message):
            logging.info(message)

        file_type = os.path.splitext(file_path)[1].lstrip('.')

        if file_type == 'csv':
            docs = get_csv_txt(file_path)
        elif file_type == 'pdf':
            docs = get_pdf_txt(file_path)
        elif file_type == 'txt':
            docs = get_txtfile_txt(file_path)

        # Split documents into smaller parts
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(docs)
        log_info(f"Split documents into {len(documents)} parts.")
        # Initialize embeddings model
        embedding = HuggingFaceEmbeddings(model_name=model_name,
                                          model_kwargs={'device': env.DEVICE })

        log_info(f"Initialized Hugging Face Embeddings with model: {model_name}")

        vector_store_path = env.VECTOR_DB_PATH + '/' + get_filename_without_extension(file_path)
        """
        为文档生成嵌入向量，如果向量数据库已存在则追加，否则创建新的向量数据库。
        """
        if faiss_db(vector_store_path):
            vector_store = FAISS.load_local(vector_store_path, embedding, allow_dangerous_deserialization=True)
            vector_store.add_documents(documents)
            log_info("Added embeddings to existing vector store.")
        else:
            vector_store = FAISS.from_documents(documents, embedding)
            log_info("Created new vector store with embeddings.")

        vector_store.save_local(vector_store_path)
        log_info(f"Saved vector store to {vector_store_path}")
        return "S", vector_store_path

    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        return "E", error_message


# Function to test file import to vectorsdb
def testing_file_to_vectorsdb(vector_store_path, query_text):
    # Log info function
    def log_info(message):
        logging.info(message)

    env = envInit.localbot()
    model_name = env.EMBEDDING_MODEL_PATH + '/' + env.EMBEDDING_MODEL
    if os.path.exists(vector_store_path):
        # Load vector store for similarity search
        vector_store = FAISS.load_local(vector_store_path, HuggingFaceEmbeddings(model_name=model_name), allow_dangerous_deserialization=True)
        log_info("Loaded vector store for similarity search.")

        # Perform similarity search
        related_docs_with_score = vector_store.similarity_search(query_text, k=4)
        log_info("Performed similarity search.")
        print(related_docs_with_score)
        for pick in related_docs_with_score:
            print(pick.page_content)
    else:
        print(f"The FAISS vector db  {vector_store_path} is not exists.")

def clear_vectorsdb(vector_store_path):
    if os.path.exists(vector_store_path):
        shutil.rmtree(vector_store_path)
        print(f"The directory {vector_store_path} has been deleted.")
    else:
        print(f"The directory {vector_store_path} does not exist.")

    # Example usage
if __name__ == "__main__":

    csv_file_path = '.\\knowledgeUploadFiles\\1_20240331212522.txt'

    # Import files to vectorsdb
    import_file_to_vectorsdb(csv_file_path)

