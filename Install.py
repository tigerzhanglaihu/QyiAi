import os
import configparser
import sys
import subprocess
import platform
import envInit
import logging  # 导入 logging 模块

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def check_git():
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        logging.info("Git is installed.")  # 记录日志
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.warning("Git is not installed.")  # 记录日志
        return False

def install_git():
    if platform.system() == "Linux":
        try:
            subprocess.run(["sudo", "apt-get", "install", "git", "-y"], check=True)
            logging.info("Git installed successfully.")  # 记录日志
            print("Git 已成功安装。")
            return True
        except subprocess.CalledProcessError:
            logging.error("Failed to install Git.")  # 记录日志
            print("安装 Git 失败。请手动安装 Git。")
            return False
    elif platform.system() == "Windows":
        logging.warning("Please install Git manually on Windows.")  # 记录日志
        print("请在 Windows 上手动安装 Git。")
        return False
    else:
        logging.error(f"Unsupported OS: {platform.system()}")  # 记录日志
        print(f"不支持的操作系统: {platform.system()}")
        return False

def check_env():
    # 检查现有的环境python环境是否 >=3.11
    if sys.version_info < (3, 11):
        print("Python 版本过旧，请升级到 3.11 或更高版本。")
        sys.exit(1)
    else:
        print(f"Python 版本 {sys.version_info} 符合要求。")

    # 检查 langchain 模块
    try:
        import langchain
        from packaging.version import parse as parse_version
        required_version = parse_version('0.1.12')
        installed_version = parse_version(langchain.__version__)

        if installed_version < required_version:
            print("langchain 版本过低，请升级。pip install transformers==4.38.2 ")
            sys.exit(1)
        else:
            print(f"langchain 版本 {installed_version} 符合要求。")
    except ImportError:
        print("未找到 langchain 模块，尝试安装...")
        try:
            subprocess.run(['pip', 'install', 'langchain==0.1.12'], check=True)
            print("langchain 模块安装成功，请重新运行程序。")
            sys.exit(1)
        except subprocess.CalledProcessError:
            print("安装 langchain 模块失败，请手动安装。pip install langchain==0.1.12")
            sys.exit(1)
    # 检查 transformers 模块 pip install transformers
    try:
        import transformers
        transformers_version = parse_version(transformers.__version__)
        required_version = parse_version('4.38.2')
        print('transformers_version:',transformers_version)
        if transformers_version < required_version:
            print("transformers 版本过低，请升级。pip install transformers==4.38.2")
            sys.exit(1)
        else:
            print(f"transformers 版本 {transformers_version} 符合要求。")

    except ImportError:
        print("未找到 transformers 模块，尝试安装...")
        try:
            subprocess.run(['pip', 'install', 'transformers==4.38.2'], check=True)
            print("transformers 模块安装成功，请重新运行程序。")
            sys.exit(1)
        except subprocess.CalledProcessError:
            print("安装 transformers 模块失败，请手动安装。pip install transformers==4.38.2")
            sys.exit(1)

    # 检查 panel 模块
    try:
        import panel
        panel_version = parse_version(panel.__version__)
        print('panel_version:', panel_version)
        required_version = parse_version('1.3.8')
        if panel_version < required_version:
            print("panel 版本过低，请升级。pip install panel==1.3.8 ")
            sys.exit(1)
        else:
            print(f"panel 版本 {panel_version } 符合要求。")
    except ImportError:
        print("未找到 panel 模块，尝试安装...")
        try:
            subprocess.run(['pip', 'install', 'panel==1.3.8'], check=True)
            print("panel 模块安装成功，请重新运行程序。")
            sys.exit(1)
        except subprocess.CalledProcessError:
            print("安装 panel 模块失败，请手动安装。pip install panel==1.3.8")
            sys.exit(1)

def clone_repo(repository_url, destination_path):
    try:
        subprocess.run(f"git clone {repository_url} {destination_path}", shell=True, check=True)
        print(f"Git repository 已成功克隆到 '{destination_path}'。")
    except subprocess.CalledProcessError as e:
        print(f"Git repository 克隆失败：{e}")

def main():
    check_env()
    config_file_path = './config.ini'
    if not os.path.isfile(config_file_path):
        logging.error(f"Configuration file '{config_file_path}' does not exist.")  # 记录日志
        print(f"错误: 配置文件 '{config_file_path}' 不存在.")
        exit(1)

    config = configparser.ConfigParser()
    config.read(config_file_path, encoding="utf8")

    try:

        MODEL_ROOT_PATH = config.get('local', 'MODEL_ROOT_PATH')
        LLM_MODEL_DOWNLOAD_URL = config.get('local', 'LLM_MODEL_DOWNLOAD_URL')
        EMBEDDING_MODEL_DOWNLOAD_URL = config.get('local', 'EMBEDDING_MODEL_DOWNLOAD_URL')
        EMBEDDING_MODEL_PATH = config.get('local', 'EMBEDDING_MODEL_PATH')
        LLM_MODEL_PATH = config.get('local', 'LLM_MODEL_PATH')
        EMBEDDING_MODEL = config.get('local', 'EMBEDDING_MODEL')
        LLM_LOCAL_MODEL = config.get('local', 'LLM_LOCAL_MODEL')
        VECTOR_DB_PATH = config.get('local', 'VECTOR_DB_PATH')

        # 确保 MODEL_ROOT_PATH 是绝对路径
        model_path = os.path.abspath(MODEL_ROOT_PATH)

        # 创建LLM目录
        llm_path = os.path.join(model_path, LLM_MODEL_PATH, LLM_LOCAL_MODEL)
        os.makedirs(llm_path, exist_ok=True)
        if not os.path.exists(llm_path):
            print(f"创建LLM目录: {llm_path}")
        else:
            print(f"LLM目录已存在: {llm_path}")

        # 创建EMBEDDING目录
        embedding_path = os.path.join(model_path, EMBEDDING_MODEL_PATH, EMBEDDING_MODEL)
        os.makedirs(embedding_path, exist_ok=True)
        if not os.path.exists(embedding_path):
            print(f"创建embedding目录: {embedding_path}")
        else:
            print(f"embedding目录已存在: {embedding_path}")

        # 创建vector db
        VECTOR_DB_PATH = os.path.join(model_path, VECTOR_DB_PATH)
        os.makedirs(VECTOR_DB_PATH, exist_ok=True)
        if not os.path.exists(VECTOR_DB_PATH):
            print(f"创建vector db目录: {embedding_path}")
        else:
            print(f"vector db目录已存在: {embedding_path}")

        # 克隆仓库
        if check_git():
            clone_repo(LLM_MODEL_DOWNLOAD_URL, llm_path)
            clone_repo(EMBEDDING_MODEL_DOWNLOAD_URL, embedding_path)
        else:
            if install_git():
                clone_repo(LLM_MODEL_DOWNLOAD_URL, llm_path)
                clone_repo(EMBEDDING_MODEL_DOWNLOAD_URL, embedding_path)
            else:
                logging.error("Failed to install Git automatically. Please handle it manually.")  # 记录日志
                print("无法自动安装 Git，请手动处理。")

    except configparser.NoOptionError as e:
        logging.error(f"Configuration error: {e}")  # 记录日志
        print(f"配置错误: {e}")
        exit(1)

if __name__ == "__main__":
    main()
    bot = envInit.localbot()
