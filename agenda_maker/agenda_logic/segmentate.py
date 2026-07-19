import argparse
import logging
from functools import reduce

import pandas as pd

from agenda_maker.common import ConfigManager, add_stage_arguments, load_stage_config
from agenda_maker.model.segmentation import SemanticTextSegmentation

logger = logging.getLogger(__name__)


def segmentation(df_whisperx: pd.DataFrame, config_manager: ConfigManager, key_text: str = "text") -> pd.DataFrame:
    """segmentationを実施"""
    list_text: list[str] = df_whisperx[key_text].to_list()
    max_segmented_text = config_manager.config.model.segmentation.max_segment_text

    if len(reduce(lambda a, b: a + b, list_text)) > max_segmented_text:
        model = SemanticTextSegmentation(config_manager=config_manager)
        list_text = model.get_result(list_text=list_text)
        logger.info(f"段落数：{len(list_text)}")
        df = pd.DataFrame(list_text, columns=[key_text])
    else:
        df = pd.DataFrame(["".join(list_text)], columns=[key_text])
        logger.info("文章分割する必要がありません")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_stage_arguments(parser, default_output_name="result")
    args = parser.parse_args()

    config_manager = load_stage_config(args.config_path, args.output_name)
    df_whisperx = pd.read_csv(config_manager.config.output.path_whisperx_file)
    df_segmented = segmentation(df_whisperx=df_whisperx, config_manager=config_manager)
    df_segmented.to_csv(config_manager.config.output.path_segmented_file, index=False)


if __name__ == "__main__":
    main()
