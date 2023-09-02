import logging
from functools import reduce
from pathlib import Path

import pandas as pd

from agenda_maker.common.config_manager import ConfigManager
from agenda_maker.model.segmentation.semantic_segmentation import SemanticTextSegmentation
from agenda_maker.model.segmentation.text_tiling import texttiling_japanese

logger = logging.getLogger()


def segmentation_logic(list_text: list[str], config_manager: ConfigManager, key_text: str = "text"):
    """segmentationを実施"""

    max_segmented_text = config_manager.config.model.segmentation.max_segmented_text
    is_segmentation = config_manager.config.tasks.is_segmentation
    path_output = Path(config_manager.config.output.path_segmented_file)

    if is_segmentation and (len(reduce(lambda a, b: a + b, list_text)) > max_segmented_text):
        text = "".join(list_text)
        list_text = texttiling_japanese(text=text, **config_manager.config.model.segmentation.texttiling)
        list_text = SemanticTextSegmentation(config_manager=config_manager).get_result(list_text=list_text)
        if _is_split(list_text):
            # TODO: 大きい章は分解する
            pass
        if _is_break(list_text):
            pass
            # TODO: 何かしら処理の必要性
        logging.info(f"段落数：{len(list_text)}")

        pd.DataFrame(list_text, columns=[key_text]).to_csv(path_output, index=False)
    elif not is_segmentation:
        logging.info(f"文章分割skip")
        list_text = pd.read_csv(Path(path_output))[key_text].to_list()
    else:
        logging.info(f"文章分割する必要がありません")
        return list_text
    return list_text


def _is_break(list_text: list) -> bool:
    return True if len(list_text) < 2 else False


def _is_split(list_text: list, max_segmented_text: int) -> bool:
    for text in list_text:
        if len(text) >= max_segmented_text:
            return True
        else:
            continue
    return False
