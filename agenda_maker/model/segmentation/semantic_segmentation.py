from functools import lru_cache, reduce
from logging import getLogger

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from agenda_maker.common.release_gpu_memory import release_gpu_memory
from agenda_maker.model.base_model import BaseModel

logger = getLogger(__name__)

__all__ = ["SemanticTextSegmentation"]


class SemanticTextSegmentation(BaseModel):

    """
    SentenceTransformerでベクトル化してcosine similarityを算出し
    類似度が閾値以上で文章を結合する。
    """

    def set_params(self) -> None:
        # parameter of  semantic segmentation
        self.threshold = self.config_manager.config.model.segmentation.semantic_segmentation.threshold
        self.th_segment_num = self.config_manager.config.model.segmentation.th_segment_num
        self.max_segment_text = self.config_manager.config.model.segmentation.max_segment_text
        self.min_segment_text = self.config_manager.config.model.segmentation.min_segment_text
        self.model_type = self.config_manager.config.model.segmentation.semantic_segmentation.model_type

    def build_model(self) -> None:
        self.set_params()
        self.load_sentence_transformer()

    def get_result(self, list_text: list[str]) -> list:
        self.build_model()
        semantic_segmentation = self._semantic_segmentation(list_text, threshold=self.threshold)
        semantic_segmentation = self.semantic_segmentation(list_text)
        if len(list_text) >= self.th_segment_num:
            semantic_segmentation = self.merge_min_text(semantic_segmentation)
        release_gpu_memory(gpu_task=self.model)
        return semantic_segmentation

    @lru_cache
    def load_sentence_transformer(self) -> None:
        self.model = SentenceTransformer(self.model_type)

    def semantic_segmentation(self, list_text: list[str]) -> list[str]:
        th_max = self.max_segment_text
        th_sim = self.threshold

        list_result = self._get_sim_len(list_text)

        while True:
            if len(list_text) <= self.th_segment_num:
                break
            is_continue = any([(value[0] >= th_sim and value[1] <= th_max) for value in list_result])

            if is_continue:
                list_text = self.combine_similar_strings(
                    list_text=list_text, list_result=list_result, th_sim=th_sim, th_max=th_max
                )
                list_result = self._get_sim_len(list_text)
            else:
                break
        return list_text

    def merge_min_text(self, list_text: list[list[str]]) -> list[str]:
        """
        文字列のリストを指定された条件に従って結合します。

        Args:
        list_text (list): 結合する文字列が格納されたリスト。
        th_min (int): チャンクとして結合するための最小文字数。
        th_max (int): チャンクとして結合後の最大文字数。

        Returns:
        list: 結合されたチャンクを格納したリスト。

        """
        th_max = self.max_segment_text
        th_min = self.min_segment_text
        merged_text = []
        current_chunk = ""

        for i in range(len(list_text)):
            text = list_text[i]

            if len(current_chunk) + len(text) <= th_max:
                current_chunk += text
            else:
                if len(current_chunk) >= th_min:
                    merged_text.append(current_chunk)
                current_chunk = text

        if len(current_chunk) >= th_min:
            merged_text.append(current_chunk)

        return merged_text

    def _get_sim_len(self, list_text: list[str]) -> list[list[float, float]]:
        list_result = []
        for i_text in range(len(list_text) - 1):
            list_result.append(
                [
                    self._get_similarity(list_text[i_text], list_text[i_text + 1])[0][0],
                    len(list_text[i_text]) + len(list_text[i_text + 1]),
                ]
            )
        return list_result

    def combine_similar_strings(self, list_text: list[str], list_result: list[list[float, float]], th_sim, th_max):
        """
        指定された条件を満たすように文字列リストを結合します。

        Args:
            list_text (list of str): 結合対象の文字列が含まれたリスト。
            list_result (list of list): 類似度と文字数の情報を含むリスト。
                各要素は [similarity, sum_len] の形式で、list_text の隣接要素間の比較結果を示します。
            th_sim (float): 類似度の閾値。この閾値以上の類似度の場合、文字列を結合します。
            th_max (int): 文字数の最大制限。結合後の文字列の文字数がこの制限を超えないようにします。

        Returns:
            list of str: 条件を満たすように結合された文字列のリスト。リストの順番は変更されません。

        Example:
            list_text = [
                '文書1のテキスト',
                '文書2のテキスト',
                # ... 他の文書のテキスト ...
            ]
            list_result = [
                [0.8, 300],  # 文書1と文書2の類似度と文字数
                [0.6, 250],  # 文書2と文書3の類似度と文字数
                # ... 他の比較結果 ...
            ]
            th_sim = 0.7
            th_max = 500

            combined_text = combine_similar_strings(list_text, list_result, th_sim, th_max)

        """
        combined_text = []
        current_text = list_text[0]

        for i in range(len(list_text) - 1):
            similarity, sum_len = list_result[i]
            next_text = list_text[i + 1]

            if similarity >= th_sim and sum_len <= th_max:
                current_text += next_text
            else:
                combined_text.append(current_text)
                current_text = next_text

        combined_text.append(current_text)
        return combined_text

    def _get_similarity(self, text1: str, text2: str) -> float:
        """テキスト1とテキスト2の文書ベクトルのコサイン類似度を計算"""
        embeding_1 = self.model.encode(text1).reshape(1, -1)
        embeding_2 = self.model.encode(text2).reshape(1, -1)

        if np.any(np.isnan(embeding_1)) or np.any(np.isnan(embeding_2)):
            return 0

        sim = cosine_similarity(embeding_1, embeding_2)
        return sim

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
            threshold += 0.01

        return new_segments

    def _index_mapping(self, segment_map) -> list[int]:
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

    def _semantic_segmentation_core(self, segments: list[str], threshold: float) -> dict:
        segment_map = [0]
        list_sim = [0.0]
        for index, (text1, text2) in enumerate(zip(segments[:-1], segments[1:])):
            sim = self._get_similarity(text1, text2)
            list_sim.append(sim[0][0])
            if sim >= threshold:
                segment_map.append(0)
            else:
                segment_map.append(1)
        list_index = self._index_mapping(segment_map)
        return {"list_index": list_index, "list_sim": list_sim}
