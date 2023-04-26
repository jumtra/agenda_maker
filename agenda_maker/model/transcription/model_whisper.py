from logging import getLogger

import whisper

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.data_object.result_transcription import ResultWhisper
from agenda_maker.model.base_model import BaseModel

logger = getLogger(__name__)


class Whisper(BaseModel):
    model_name = "model_whisper"

    def set_params(self) -> None:
        self.model_type = (
            self.config_manager.config.model.transcription.whisper.model_type
        )
        self.verbose = self.config_manager.config.model.transcription.whisper.verbose
        self.condition_on_previous_text = (
            self.config_manager.config.model.transcription.whisper.condition_on_previous_text
        )
        self.logprob_threshold = (
            self.config_manager.config.model.transcription.whisper.logprob_threshold
        )
        self.no_speech_threshold = (
            self.config_manager.config.model.transcription.whisper.no_speech_threshold
        )
        logger.info("Setting Parameter")

    def build_model(self) -> None:
        self.set_params()
        logger.info("Build Model")
        self.model = whisper.load_model(self.model_type).to(self.device)

    def release_memory(self) -> None:
        release_gpu_memory(self.model)

    def get_result(self, input_path: str, is_translate: bool = False) -> ResultWhisper:
        task = "translate" if is_translate else "transcribe"
        result = self.model.transcribe(
            audio=input_path,
            verbose=self.verbose,
            condition_on_previous_text=self.condition_on_previous_text,
            logprob_threshold=self.logprob_threshold,
            no_speech_threshold=self.no_speech_threshold,
            language="ja",
            task=task,
            beam_size=10,
        )
        return ResultWhisper(
            engwords_per_line=self.config_manager.config.model.transcription.engwords_per_line,
            jpwords_per_line=self.config_manager.config.model.transcription.jpwords_per_line,
            is_translate=is_translate,
            language=result["language"],
            transcript_text=result["text"],
            list_result=result["segments"],
        )
