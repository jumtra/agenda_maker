import logging
from functools import reduce
from pathlib import Path

import pandas as pd

from agenda_maker.common import ConfigManager
from agenda_maker.model.segmentation import SemanticTextSegmentation, texttiling_japanese

logger = logging.getLogger()


import argparse


def segmentation(df_whisperx: pd.DataFrame, config_manager: ConfigManager, key_text: str = "text") -> pd.DataFrame:
    """segmentationを実施"""
    list_text: list[str] = df_whisperx[key_text].to_list()

    max_segmented_text = config_manager.config.model.segmentation.max_segment_text

    if len(reduce(lambda a, b: a + b, list_text)) > max_segmented_text:
        # NOTE texttilingない方がいい感じに分割できる
        # text = "".join(list_text)
        # list_text = texttiling_japanese(text=text, **config_manager.config.model.segmentation.texttiling)
        _model = SemanticTextSegmentation(config_manager=config_manager)
        list_text = _model.get_result(list_text=list_text)
        logging.info(f"段落数：{len(list_text)}")
        df = pd.DataFrame(list_text, columns=[key_text])
    else:
        df = pd.DataFrame(["".join(list_text)], columns=[key_text])
        logging.info(f"文章分割する必要がありません")
    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-config", "--config_path", default="agenda_maker/config/config.yaml", type=str)
    parser.add_argument("-output", "--output_name", default="test", type=str)

    args = parser.parse_args()
    config_path = args.config_path
    config_dir = str("/".join(Path(config_path).parts[:-1]))
    config_yaml_path = str(Path(config_path).parts[-1])
    config_manager = ConfigManager.from_yaml(
        config_yaml_path=config_yaml_path,
        config_dir=config_dir,
    )
    output = args.output_name
    config_manager.config.output.output_dir = Path(config_manager.config.output.output_dir_base) / output

    Path(config_manager.config.output.output_dir).mkdir(exist_ok=True, parents=True)

    df_whisperx = pd.read_csv(config_manager.config.output.path_whisperx_file)
    df_segmented = segmentation(df_whisperx=df_whisperx, config_manager=config_manager)
    df_segmented.to_csv(config_manager.config.output.path_segmented_file, index=False)


if __name__ == "__main__":
    main()
