import argparse
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from agenda_maker.common import ConfigManager, release_gpu_memory
from agenda_maker.model.summarization import Elyza


def preprocess(text: str) -> str:
    """ノイズ除去"""
    if "要約:" in text:
        text = text.split("要約:")[-1]
    text = re.sub(r"【.*】", "", text)
    text = re.sub(r"（.*）", "", text)
    text = re.sub(r"「.*」", "", text)
    text = re.sub(r"<.*>", "", text)
    text = re.sub(r"＜.*＞", "", text)
    text = re.sub(r"[［］\[\]]", " ", text)  # ［］の除去
    text = re.sub(r"[@＠]\w+", "", text)  # メンションの除去
    text = re.sub(r"https?:\/\/.*?[\r\n ]", "", text)  # URLの除去
    text = re.sub(r"　", " ", text)  # 全角空白の除去
    text = text.replace("\u200b", "")
    text = text.replace("/", "")
    text = text.replace("-", "")
    text = text.replace("\n", "")
    return text


def summarize(df_segmented: pd.DataFrame, config_manager: ConfigManager, key_text: str = "text") -> pd.DataFrame:
    list_text = df_segmented[key_text].to_list()
    list_result = []
    for text in tqdm(list_text, desc="Summarize"):
        if len(text) <= config_manager.config.model.segmentation.min_segment_text:
            continue
        # Summarize
        model = Elyza(config_manager=config_manager)
        release_gpu_memory(model)
        _text = model.get_result(text, task="summarize")
        _text = preprocess(_text)

        list_result.append(_text)

    text_result = "".join(list_result)
    model = Elyza(config_manager=config_manager)
    release_gpu_memory(model)
    _text = model.get_result(text_result, task="punctuation")
    _text = preprocess(_text)
    list_result = [_text]

    model = Elyza(config_manager=config_manager)
    release_gpu_memory(model)
    _text = model.get_result(text_result, task="last_summarize")
    _text = preprocess(_text)
    list_result.append(_text)
    df = pd.DataFrame(list_result, columns=[key_text])
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

    df_segmented = pd.read_csv(config_manager.config.output.path_segmented_file)
    df_summarized = summarize(df_segmented=df_segmented, config_manager=config_manager)

    df_summarized.to_csv(config_manager.config.output.path_summarized_file, index=False)


if __name__ == "__main__":
    main()
