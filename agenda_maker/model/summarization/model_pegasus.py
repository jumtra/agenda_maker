from logging import getLogger
from typing import Tuple

from transformers import PegasusForConditionalGeneration, PegasusTokenizer

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.model.base_model import BaseModel

logger = getLogger(__name__)


class Pegasus(BaseModel):
    model_name = "model_pegasus"

    def set_params(self) -> None:
        self.model_type = (
            self.config_manager.config.model.summarization.pegasus.model_type
        )
        self.tokenizer_type = (
            self.config_manager.config.model.summarization.pegasus.tokenizer_type
        )
        self.min_length = (
            self.config_manager.config.model.summarization.pegasus.min_length
        )
        self.max_length = (
            self.config_manager.config.model.summarization.pegasus.max_length
        )
        self.min_length = (
            self.config_manager.config.model.summarization.pegasus.min_length
        )
        self.use_first = (
            self.config_manager.config.model.summarization.pegasus.use_first
        )
        self.num_beams = (
            self.config_manager.config.model.summarization.pegasus_x.num_beams
        )
        self.no_repeat_ngram_size = (
            self.config_manager.config.model.summarization.pegasus_x.no_repeat_ngram_size
        )
        logger.info("Setting Parameter")

    def build_model(self) -> None:
        self.set_params()
        logger.info("Build Model")
        self.model = PegasusForConditionalGeneration.from_pretrained(
            self.model_type
        ).to(self.device)

        logger.info("Build Tokenizer")
        self.tokenizer = PegasusTokenizer.from_pretrained(self.tokenizer_type)

    def _gen_text_length_adjuster(self, text: str) -> Tuple[bool, int, int]:
        # 要約する必要がないとき
        if len(text) < self.min_length:
            is_summary = False
            max_length = 0
            min_length = 0
        elif len(text) < self.max_length:
            is_summary = True
            max_length = max(int(len(text) / 2), 300)
            min_length = min(int(max_length / 2), self.min_length)
        else:
            is_summary = True
            max_length = self.max_length
            min_length = self.min_length
        return is_summary, max_length, min_length

    def _run(self, text: str) -> str:
        logger.info(f"Summaryze_{self.model_name}")
        is_summary, max_length, min_length = self._gen_text_length_adjuster(text)
        if is_summary:
            inputs = self.tokenizer([text], return_tensors="pt", truncation=True).to(
                self.device
            )
            summary_ids = self.model.generate(  # type: ignore
                inputs["input_ids"],
                num_beams=self.num_beams,
                max_length=max_length,
                min_length=min_length,
                no_repeat_ngram_size=self.no_repeat_ngram_size,
                # early_stopping=True,
            )
            generate_text = [
                self.tokenizer.decode(
                    g, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )
                for g in summary_ids
            ]
            generate_text = generate_text[0]
        else:
            logger.info(f"要約skip")
            generate_text = text
        return generate_text

    def get_result(self, list_text: list) -> list:
        list_gen_text = []
        for text in list_text:
            gen_text = self._run(text)
            list_gen_text.append(gen_text)

        release_gpu_memory(self.model)
        release_gpu_memory(self.tokenizer)
        return list_gen_text
