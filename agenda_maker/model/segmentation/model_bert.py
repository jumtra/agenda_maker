from functools import reduce
from logging import getLogger
from typing import List, Tuple

from transformers import pipeline

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.data_object.result_transcription import ResultWhisper
from agenda_maker.model.base_model import BaseModel

logger = getLogger()


class BertClassify(BaseModel):
    model_name = "model_transformer_text_classify"

    def set_params(self) -> None:
        self.model_type = self.config_manager.config.model.segmentation.bert.model_type
        self.max_segment_text = (
            self.config_manager.config.model.segmentation.bert.max_segment_text
        )
        self.threshold_step = (
            self.config_manager.config.model.segmentation.bert.threshold_step
        )
        logger.info("Setting Parameter")

    def build_model(self) -> None:
        self.set_params()
        logger.info("Build Model")
        self.model = pipeline(
            "text-classification",
            model=self.model_type,
        )

    def _calc_score(self, text_a: str, text_b: str, len_str: int = 250) -> float:
        """4つの観点で文の塊の類似度を算出"""

        # 文ブロックhead部分同士の比較score
        score_head = self.model(f"{text_a[:len_str]}[SEP]{text_b[:len_str]}")[0][
            "score"
        ]
        # 文ブロックtail部分同士の比較score
        score_tail = self.model(f"{text_a[-len_str:]}[SEP]{text_b[-len_str:]}")[0][
            "score"
        ]
        # 文節境界付近のscore
        score_sep = self.model(f"{text_a[-len_str:]}[SEP]{text_b[:len_str]}")[0][
            "score"
        ]
        # 文ブロックheadとtailの比較score
        score_head_tail = self.model(f"{text_a[:len_str]}[SEP]{text_b[-len_str:]}")[0][
            "score"
        ]

        score = (score_head + score_tail + score_sep + score_head_tail) / 4
        return score

    def _get_list_label(self, list_score: list, THRESHOLD: float) -> list:
        """THRESHOLDを超えている文節に類似ラベルTRUEを付与"""
        list_label = [True if score >= THRESHOLD else False for score in list_score]
        return list_label

    def _get_list_text(self, list_segmented_text: list, list_label: list) -> list:
        """類似ラベルを元に文章の結合"""

        list_text = []
        texts = list_segmented_text[0]
        for i in range(len(list_label)):
            if list_label[i]:
                texts += list_segmented_text[i + 1]
            else:
                list_text.append(texts)
                texts = list_segmented_text[i + 1]
        if len(list_text) == 0:
            return [texts]
        else:
            list_text.append(texts)
            return list_text

    def _get_threshold(self, list_text: list, THRESHOLD: float) -> Tuple[float, bool]:
        """リスト内の文章がmax_segment_textを超えている場合、閾値を上方修正して、さらに、細かく分割する。"""
        is_over = False
        for text in list_text:
            if len(text) >= self.max_segment_text:
                THRESHOLD += self.threshold_step
                if THRESHOLD > 1.0:
                    is_over = False
                else:
                    is_over = True
                break
            else:
                continue
        return THRESHOLD, is_over

    def _get_list_score(self, list_text: list) -> list:
        """scoreの計算"""
        list_score = [
            self._calc_score(list_text[i], list_text[i - 1])
            for i in range(len(list_text) - 1)
        ]
        return list_score

    def _get_max_segment_text(self, list_text: List[str]) -> int:
        len_text = len(reduce(lambda a, b: a + b, list_text))
        len_seg_text = int(
            len_text / self.config_manager.config.model.segmentation.segment_num
        )
        if self.max_segment_text > len_seg_text:
            return max(len_seg_text - 500, int(self.max_segment_text / 2) + 1000)
        else:
            return self.max_segment_text

    def get_result(self, list_text: List[str], THRESHOLD: float = 0.70) -> list:

        list_score = self._get_list_score(list_text=list_text)
        self.max_segment_text = self._get_max_segment_text(list_text=list_text)

        is_over = True

        while is_over:
            list_label = self._get_list_label(
                list_score=list_score, THRESHOLD=THRESHOLD
            )
            list_seg_text = self._get_list_text(
                list_segmented_text=list_text, list_label=list_label
            )
            THRESHOLD, is_over = self._get_threshold(
                list_text=list_seg_text, THRESHOLD=THRESHOLD
            )
        release_gpu_memory(self.model)
        return list_seg_text
