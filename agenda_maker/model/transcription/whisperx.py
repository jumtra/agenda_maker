import re
import unicodedata
from dataclasses import dataclass
from logging import getLogger
from typing import Optional

import pandas as pd
import whisperx

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.model.base_model import BaseModel

logger = getLogger(__name__)

__all__ = ["WhisperX"]


@dataclass
class ResultWhisper:
    """Whisperの結果を保存するデータクラス
    segments: whisperxの結果
    word_segments: whisperxの結果
    language: 使用言語
    transcript_text: 文字起こしされたテキスト
    """

    segments: list[dict[str, tuple[float, str]]]
    word_segments: list[dict[str, tuple[float, str]]]
    language: str
    df_result: Optional[pd.DataFrame] = None
    df_word_seg: Optional[pd.DataFrame] = None
    df_original: Optional[pd.DataFrame] = None

    def remove_noise(self, text: str) -> str:
        """ノイズ除去"""
        text = re.sub(r"【.*】", "", text)
        text = re.sub(r"（.*）", "", text)
        text = re.sub(r"「.*」", "", text)
        text = re.sub(r"[［］\[\]]", " ", text)  # ［］の除去
        text = re.sub(r"[@＠]\w+", "", text)  # メンションの除去
        text = re.sub(r"https?:\/\/.*?[\r\n ]", "", text)  # URLの除去
        text = re.sub(r"　", " ", text)  # 全角空白の除去
        text = text.replace("\u200b", "")
        text = text.replace("おだしょー", "")  # whisper特有のバグワード
        text = text.replace("/", "")
        return text

    def remove_min_text(self, text: str, min_length: int) -> str:
        if len(text) <= min_length:
            return ""
        else:
            return text

    def remove_duplication(self, df_result: pd.DataFrame) -> pd.DataFrame:
        """文の重複を削除（繰り返して完全一致の文章があったら1つを残して削除する）"""
        return df_result.drop_duplicates(subset="text", keep="first").reset_index(drop=True)

    def remove_unicode(self, text: str, form="NFKC") -> str:
        normalized_text = unicodedata.normalize(form, text)
        return normalized_text

    def __post_init__(self) -> None:
        df_segments = pd.DataFrame(self.segments)
        self.df_word_seg = pd.DataFrame(self.word_segments)
        self.df_original = df_segments.copy()
        list_text = df_segments["text"].to_list()

        for list_id, text in enumerate(list_text):
            text = self.remove_unicode(text)
            text = self.remove_noise(text)
            text = self.remove_min_text(text, 5)
            if len(text) == 0:
                list_text[list_id] = float("nan")
            else:
                list_text[list_id] = text
        # 文の重複を削除
        df_segments.loc[:, "text"] = list_text
        df_segments = self.remove_duplication(df_segments)
        # 文の欠損削除
        df_result = df_segments.dropna(subset="text", axis=0).reset_index(drop=True)
        self.df_result = df_result


class WhisperX(BaseModel):
    """WhisperX を使った文字起こしと話者分離をするモデル"""

    def build_model(self) -> None:
        self.set_params()
        logger.info("Build Model")
        self.model = whisperx.load_model(self.model_type, self.device, compute_type=self.compute_type)

    def set_params(self):
        whisper_params = self.config_manager.config.model.whisperx.whisper
        self.model_type = whisper_params.model_type
        self.batch_size = whisper_params.batch_size
        self.compute_type = whisper_params.compute_type

        diarization_params = self.config_manager.config.model.whisperx.diarization
        self.min_speakers = diarization_params.min_speakers
        self.max_speakers = diarization_params.max_speakers

        logger.info("Setting Parameter")

    def get_result(self, input_path: str) -> ResultWhisper:
        self.build_model()
        audio = whisperx.load_audio(input_path)

        result = self.model.transcribe(audio, batch_size=self.batch_size, print_progress=True)
        segments = result["segments"]
        language = result["language"]
        release_gpu_memory(self.model)
        # 2. Align whisper output
        model_a, metadata = whisperx.load_align_model(language_code=language, device=self.device)
        result = whisperx.align(
            segments,
            model_a,
            metadata,
            audio,
            self.device,
            return_char_alignments=False,
            print_progress=True,
            total_segments=len(segments),
        )
        release_gpu_memory(model_a)

        # 3. Assign speaker labels
        diarize_model = whisperx.DiarizationPipeline(device=self.device)

        # add min/max number of speakers if known
        diarize_segments = diarize_model(input_path, min_speakers=self.min_speakers, max_speakers=self.max_speakers)
        release_gpu_memory(diarize_model)

        result = whisperx.assign_word_speakers(diarize_segments, result)
        return ResultWhisper(segments=result["segments"], word_segments=result["word_segments"], language=language)
