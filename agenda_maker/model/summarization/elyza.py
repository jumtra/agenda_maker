from logging import getLogger
from typing import Literal

from llama_cpp import Llama

from agenda_maker.model.base_model import BaseModel

from .prompt import input_from_prompt

logger = getLogger(__name__)


class Elyza(BaseModel):
    """ELYZA Llama2 を使った要約・文章校正モデル"""

    def build_model(self) -> None:
        if getattr(self, "model", None) is not None:
            return

        self.set_params()
        logger.info("Build Model")

        # 使うdeviceは、llama.cppのコンパイル方法次第
        if self.is_gpu and self.device == "cuda":
            logger.info("GPUで実行")
            self.model = Llama(model_path=self.model_type, n_ctx=self.n_ctx, n_gpu_layers=self.n_gpu_layers)
        else:
            logger.info("CPUで実行")
            self.model = Llama(model_path=self.model_type, n_ctx=self.n_ctx)

    def set_params(self) -> None:
        summarize_params = self.config_manager.config.model.summarization
        self.model_type = summarize_params.model_path
        self.n_ctx = summarize_params.n_ctx
        self.n_gpu_layers = summarize_params.n_gpu_layers
        self.is_gpu = summarize_params.is_gpu_compile
        self.params = summarize_params.params

        logger.info("Setting Parameter")

    def get_result(
        self,
        text: str,
        task: Literal["summarize", "punctuation", "last_summarize", "default"],
    ) -> str:
        self.build_model()
        prompt = input_from_prompt(text=text, task=task)
        output = self.model(prompt, **self.params)
        return output["choices"][0]["text"]
