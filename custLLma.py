from typing import Any, List, Mapping, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.language_models.llms import LLM
import torch
import envInit

class CustomLLM(LLM):
    model_name : str
    @property
    def _llm_type(self) -> str:
        return "custom"
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        response = ''
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        else:
            env = envInit.localbot()
            model_name =  env.LLM_MODEL_PATH + "/" + env.LLM_LOCAL_MODEL
            print('使用',env.DEVICE,'进行计算！')
            #主代码
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).to(env.DEVICE)
            model = model.float()
            response, _ = model.chat(tokenizer, prompt)  # 这里演示未使用流式接口. stream_chat()
            print('prompt:',prompt)
        return response
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self.model_name}


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    model_name = ".\\Model\\chatglm3-6b"
    llm = CustomLLM(model_name=model_name)
    print(llm.invoke('你好？'))
