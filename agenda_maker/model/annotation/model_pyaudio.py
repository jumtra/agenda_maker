from logging import getLogger
from pathlib import Path

from pyannote.audio import Pipeline

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.data_object.result_annotation import ResultAnnotation
from agenda_maker.model.base_model import BaseModel

logger = getLogger(__name__)


class PyaudioModel(BaseModel):
    model_name = "model_pyaudio"

    def set_params(self) -> None:
        logger.info("Setting Parameter")
        self.min_speakers = self.config_manager.config.model.annotation.min_speakers
        self.max_speakers = self.config_manager.config.model.annotation.max_speakers

    def build_model(self) -> None:
        self.set_params()
        logger.info("Build Model")
        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

    def get_result(self, path_input: str) -> ResultAnnotation:
        logger.info("Annotate")

        if isinstance(self.min_speakers, int) and isinstance(self.max_speakers, int):
            logger.info("speaker人数を指定して実行")
            diarization = self.pipeline(
                Path(path_input),
                min_speakers=self.min_speakers,
                max_speakers=self.max_speakers,
            )
        else:
            logger.info("speaker人数の設定はありません")
            diarization = self.pipeline(
                Path(path_input),
            )

        result_str = str(diarization)
        list_result = result_str.split("\n")
        # GPU メモリーの解放
        release_gpu_memory(diarization)
        return ResultAnnotation(
            model_name=self.model_name,
            result_str=result_str,
            list_result=list_result,
        )
