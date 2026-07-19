import argparse

import pandas as pd
from tqdm import tqdm

from agenda_maker.common import ConfigManager, add_stage_arguments, load_stage_config, release_gpu_memory, remove_text_noise
from agenda_maker.model.summarization import Elyza


def clean_summary_text(text: str) -> str:
    """要約結果のノイズ除去"""
    return remove_text_noise(
        text,
        strip_summary_prefix=True,
        strip_angle_brackets=True,
        strip_hyphen=True,
        strip_newlines=True,
    )


def summarize(df_segmented: pd.DataFrame, config_manager: ConfigManager, key_text: str = "text") -> pd.DataFrame:
    list_text = df_segmented[key_text].to_list()
    list_result = []
    model = Elyza(config_manager=config_manager)

    try:
        for text in tqdm(list_text, desc="Summarize"):
            if len(text) <= config_manager.config.model.segmentation.min_segment_text:
                continue
            summarized = model.get_result(text, task="summarize")
            list_result.append(clean_summary_text(summarized))

        text_result = "".join(list_result)
        punctuated = clean_summary_text(model.get_result(text_result, task="punctuation"))
        last_summary = clean_summary_text(model.get_result(text_result, task="last_summarize"))
        return pd.DataFrame([punctuated, last_summary], columns=[key_text])
    finally:
        release_gpu_memory(model)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_stage_arguments(parser, default_output_name="result")
    args = parser.parse_args()

    config_manager = load_stage_config(args.config_path, args.output_name)
    df_segmented = pd.read_csv(config_manager.config.output.path_segmented_file)
    df_summarized = summarize(df_segmented=df_segmented, config_manager=config_manager)
    df_summarized.to_csv(config_manager.config.output.path_summarized_file, index=False)


if __name__ == "__main__":
    main()
