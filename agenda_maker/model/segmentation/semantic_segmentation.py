from functools import lru_cache, reduce
from logging import getLogger

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.model.base_model import BaseModel

logger = getLogger(__name__)


class SemanticTextSegmentation(BaseModel):

    """
    texttilingで分割された文章を順にSentenceTransformerでベクトル化してcosine similarityを算出し
    類似度が閾値以上で文章を結合する。
    """

    def set_params(self) -> None:
        # parameter of  semantic segmentation
        self.threshold = self.config_manager.config.model.segmentation.semantic_segmentation.threshold
        self.threshold_step = self.config_manager.config.model.segmentation.semantic_segmentation.threshold_step
        self.max_segment_text = self.config_manager.config.model.segmentation.semantic_segmentation.max_segment_text
        self.model_type = self.config_manager.config.model.segmentation.semantic_segmentation.model_type

    def build_model(self) -> None:
        self.set_params()
        self.load_sentence_transformer()

    def get_result(self, list_text: list[str]) -> list:
        self.max_segment_text = self._get_max_segment_text(list_text=list_text)
        semantic_segmentation = self._semantic_segmentation(list_text, self.threshold)
        release_gpu_memory(gpu_task=self.model)
        return semantic_segmentation

    @lru_cache
    def load_sentence_transformer(self) -> None:
        self.model = SentenceTransformer(self.model_type)

    def _semantic_segmentation_core(self, segments: list[str], threshold: float) -> dict:
        segment_map = [0]
        list_sim = [0.0]
        for index, (text1, text2) in enumerate(zip(segments[:-1], segments[1:])):
            sim = self._get_similarity(text1, text2)
            list_sim.append(sim)
            if sim >= threshold:
                segment_map.append(0)
            else:
                segment_map.append(1)
        list_index = self._index_mapping(segment_map)
        return {"list_index": list_index, "list_sim": list_sim}

    def _get_max_segment_text(self, list_text: list) -> int:
        len_text = len(reduce(lambda a, b: a + b, list_text))
        len_seg_text = int(len_text / self.config_manager.config.model.segmentation.segment_num)
        if self.max_segment_text > len_seg_text:
            return max(len_seg_text - 500, int(self.max_segment_text / 2) + 1000)
        else:
            return self.max_segment_text

    def _semantic_segmentation(self, segments: list[str], threshold: float) -> list:
        new_segments = []
        is_over = True

        while is_over:
            dict_result = self._semantic_segmentation_core(segments=segments, threshold=threshold)
            list_index = dict_result["list_index"]
            list_sim = dict_result["list_sim"]
            for index_i in list_index:
                seg = " ".join([segments[i] for i in index_i])
                new_segments.append(seg)
                if len(seg) > self.max_segment_text:
                    if threshold > 1.0:
                        is_over = False
                    else:
                        is_over = True
                        new_segments = []
                        break
                else:
                    is_over = False
            threshold += self.threshold_step

        return new_segments

    def _index_mapping(self, segment_map) -> list[list[int]]:
        """分割された文のインデックスをリストでまとめる"""
        index_list = []
        temp = []
        for index, i in enumerate(segment_map):
            if i == 1:
                index_list.append(temp)
                temp = [index]
            else:
                temp.append(index)
        index_list.append(temp)
        return index_list

    def _get_similarity(self, text1: str, text2: str) -> float:
        """テキスト1とテキスト2の文書ベクトルのコサイン類似度を計算"""
        embeding_1 = self.model.encode(text1).reshape(1, -1)
        embeding_2 = self.model.encode(text2).reshape(1, -1)

        if np.any(np.isnan(embeding_1)) or np.any(np.isnan(embeding_2)):
            return 1

        sim = cosine_similarity(embeding_1, embeding_2)
        return sim
