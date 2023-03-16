from logging import getLogger
from typing import Dict, List

from nltk.tokenize.texttiling import TextTilingTokenizer

from agenda_maker.model.base_model import BaseModel

logger = getLogger(__name__)

# Reffrence :https://github.com/maxent-ai/converse
class TextTilling(BaseModel):

    """
    Segment a call transcript based on topics discussed in the call using
    TextTilling with Sentence Similarity via sentence transformer.
    """

    model_name = "model_text_tilling"

    def set_params(self) -> None:
        # parameter of  text tiling
        self.w = self.config_manager.config.model.segmentation.text_tiling.w
        self.k = self.config_manager.config.model.segmentation.text_tiling.k
        self.smoothing_width = (
            self.config_manager.config.model.segmentation.text_tiling.smoothing_width
        )
        self.smoothing_rounds = (
            self.config_manager.config.model.segmentation.text_tiling.smoothing_rounds
        )

    def build_model(self) -> None:
        self.set_params()

    def get_result(self, list_text: List[str]) -> list:
        text_tiling = self._text_tiling(list_text=list_text)

        return text_tiling

    def _text_tiling(self, list_text: list) -> list:
        """nltkのtext_tilingで分割したテキストを取得"""
        tt_false = TextTilingTokenizer(
            w=self.w,
            k=self.k,
            smoothing_width=self.smoothing_width,
            smoothing_rounds=self.smoothing_rounds,
            demo_mode=False,
        )
        # tt_true = TextTilingTokenizer(
        #    w=self.w,
        #    k=self.k,
        #    smoothing_width=self.smoothing_width,
        #    smoothing_rounds=self.smoothing_rounds,
        #    demo_mode=True,
        # )

        # text tilingに入れる形式に変換
        text = "\n\n\t".join(list_text)

        # scoreの獲得
        # gaps_scores, smooth_scored, depth_scores, segment_boundaries = tt_true.tokenize(
        #    text=text
        # )
        segment = tt_false.tokenize(text=text)
        list_segment = [i.replace("\n\n\t", " ") for i in segment]
        return list_segment
