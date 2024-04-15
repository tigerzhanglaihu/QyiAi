import configparser
import subprocess
import platform
import re

class localbot():
    def __init__(self, **params):
        config_file_path = 'config.ini'
        # 创建配置解析器对象
        config = configparser.ConfigParser()
        # 读取配置文件
        config.read(config_file_path,encoding="utf8")
        try:
            #根目录
            self.MODEL_ROOT_PATH = config.get('local', 'MODEL_ROOT_PATH')
            # LLM 下载路径
            self.LLM_MODEL_DOWNLOAD_URL = config.get('local','LLM_MODEL_DOWNLOAD_URL')
            # EMBEDDING 下载路径
            self.EMBEDDING_MODEL_DOWNLOAD_URL = config.get('local','EMBEDDING_MODEL_DOWNLOAD_URL')
            # EMBEDDING 模型路径
            self.EMBEDDING_MODEL_PATH = config.get('local',"EMBEDDING_MODEL_PATH")
            # LLM 本地模型路径
            self.LLM_MODEL_PATH = config.get('local',"LLM_MODEL_PATH")
            # 选用的 Embedding 名称
            self.EMBEDDING_MODEL = config.get('local',"EMBEDDING_MODEL")
            # 提供一个离线和在线的模型
            self.LLM_LOCAL_MODEL = config.get('local',"LLM_LOCAL_MODEL")
            # 提供一个在线的模型
            self.LLM_ONLINE_MODEL = config.get('local', "LLM_ONLINE_MODEL")
            # 本地向量数据库路径
            self.VECTOR_DB_PATH = config.get('local', "VECTOR_DB_PATH")
            # 文件上传路径
            self.FILE_UPLOAD_PATH = config.get('local', "FILE_UPLOAD_PATH")
            # 检查GPU是否可用
            self.DEVICE = self.check_gpu()
        except:
            print('读取配置文件错误，请检查项目是否完整！')

    def check_gpu(self):
        system_info = {
            'system': platform.system(),
            'release': platform.release(),
            'architecture': platform.architecture()[0]
        }
        platform_type= system_info['system']

        """
        检查 CUDA 是否安装正确。
        """
        try:
            output = subprocess.check_output(["nvcc", "--version"]).decode("utf-8")
            version_match = re.search(r"release (\d+\.\d+)", output)
            if version_match:
                cuda_version = float(version_match.group(1))
            else:
                print('cuda未正常安装！')
        except FileNotFoundError:
            print('cuda未正常安装！')

        """
        获取 GPU 显存大小。
        """
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"]).decode("utf-8")
            gpu_memory = int(output.strip().split()[0])
        except (FileNotFoundError, subprocess.CalledProcessError):
            print('nvidia-smi未正常安装')

        """
        检查 GPU 是否可用，根据显存大小确定使用 CPU 还是 GPU。
        """
        if platform_type == 'Windows':
            if cuda_version:
                if gpu_memory and gpu_memory >= 8 * 1024:  # 大于等于8GB
                    return "gpu"
                else:
                    return "cpu"
            else:
                print("CUDA 未正确安装，无法使用 GPU。使用 CPU。")
                return None
        elif platform_type == 'Linux':
            if cuda_version:
                if gpu_memory and gpu_memory >= 8 * 1024:  # 大于等于8GB
                    return "gpu"
                else:
                    return "cpu"
            else:
                return "CUDA 未正确安装，无法使用 GPU。使用 CPU。"
        else:
            print("未知系统类型，无法确定使用的驱动。")
            return None

if __name__ == "__main__":
    bot = localbot()
