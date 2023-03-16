from logging import getLogger

from transformers import MarianMTModel, MarianTokenizer

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.model.base_model import BaseModel

logger = getLogger()


class MarianMt(BaseModel):
    model_name = "model_marianmt"

    def set_params(self) -> None:
        self.model_type = self.config_manager.config.model.translation.marian.model_type
        self.tokenizer_type = (
            self.config_manager.config.model.translation.marian.tokenizer_type
        )
        self.max_length = self.config_manager.config.model.translation.marian.max_length
        self.input_max_length = (
            self.config_manager.config.model.translation.marian.input_max_length
        )
        self.num_beams = self.config_manager.config.model.translation.marian.num_beams
        self.no_repeat_ngram_size = (
            self.config_manager.config.model.translation.marian.no_repeat_ngram_size
        )
        logger.info("Setting Parameter")

    def build_model(self) -> None:
        self.set_params()
        logger.info("Build Model")
        self.model = MarianMTModel.from_pretrained(
            self.model_type,
        ).to(self.device)

        logger.info("Build Tokenizer")
        self.tokenizer = MarianTokenizer.from_pretrained(self.tokenizer_type)

    def _run(self, text: str) -> str:
        logger.info(f"Translate_{self.model_name}")
        encoded_zh = self.tokenizer(
            text, return_tensors="pt", max_length=self.input_max_length, truncation=True
        ).to("cuda")
        generated_tokens = self.model.generate(
            **encoded_zh,
            max_new_tokens=self.max_length,
            no_repeat_ngram_size=self.no_repeat_ngram_size,
            early_stopping=True,
            num_beams=self.num_beams,
        )
        output_text = self.tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )
        return output_text[0]

    def get_result(self, list_text: list) -> list:
        list_gen_text = []
        for text in list_text:
            if len(text) >= self.input_max_length:
                continue
            else:
                gen_text = self._run(text)
                list_gen_text.append(gen_text)

        release_gpu_memory(self.model)
        release_gpu_memory(self.tokenizer)
        return list_gen_text
