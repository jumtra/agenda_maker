from typing import Dict

from .annotation.model_pyaudio import PyaudioModel
from .base_model import BaseModel
from .segmentation.model_bert import BertClassify
from .segmentation.model_semantic_text_segmentation import SemanticTextSegmentation
from .segmentation.model_text_tilling import TextTilling
from .summarization.model_pegasus import Pegasus
from .summarization.model_pegasus_x import Pegasus_X
from .transcription.model_whisper import Whisper
from .translation.model_marian_mt import MarianMt

_dict_name_map_model_class: Dict[str, BaseModel] = {
    PyaudioModel.model_name: PyaudioModel,
    Whisper.model_name: Whisper,
    SemanticTextSegmentation.model_name: SemanticTextSegmentation,
    BertClassify.model_name: BertClassify,
    TextTilling.model_name: TextTilling,
    Pegasus.model_name: Pegasus,
    Pegasus_X.model_name: Pegasus_X,
    MarianMt.model_name: MarianMt,
}


def get_model_class(model_name: str) -> BaseModel:
    """モデル名からモデルクラスを取得する"""
    return _dict_name_map_model_class[model_name]
