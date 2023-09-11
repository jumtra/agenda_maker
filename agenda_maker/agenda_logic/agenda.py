import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from agenda_maker.common import ConfigManager


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-config", "--config_path", default="agenda_maker/config/config.yaml", type=str)
    parser.add_argument("-output", "--output_name", default="result", type=str)

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
    df_summarized = pd.read_csv(config_manager.config.output.path_summarized_file)
    df_whisperx = pd.read_csv(config_manager.config.output.path_whisperx_file)
    file_name = config_manager.config.output.path_agenda_file
    format2agenda(df_summarized=df_summarized, df_whisperx=df_whisperx, file_name=file_name)


def format2agenda(
    df_summarized: pd.DataFrame,
    df_whisperx: pd.DataFrame,
    file_name: str,
) -> None:
    """議事録のフォーマットに修正"""
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().strftime("%a")
    list_speaker = _get_list_speaker(df=df_whisperx)
    list_summary = _get_list_summary(df=df_summarized)
    list_transcript = _get_list_transcript(df=df_whisperx)
    _agenda_format(
        file_name=file_name,
        today=today,
        weekday=weekday,
        list_speaker=list_speaker,
        list_summary=list_summary,
        list_transcript=list_transcript,
    )


def _agenda_format(
    file_name: str,
    today: str,
    weekday: str,
    list_speaker: list,
    list_summary: list,
    list_transcript: list,
) -> None:
    with open(f"{file_name}.md", "w") as f:
        f.write("## 基本情報\n")
        f.write("【議事名】\txxxxx \n")
        f.write(f"\n【日　時】\t{today} ({weekday}) \n")
        f.write(f"\n【場　所】\tMeet (Web Meeting) \n")
        f.write(f"\n【出席者（敬称略）】\n")

        for speaker in list_speaker:
            f.write(f"- {speaker}様 \n")
        # f.write("\n")
        # f.write(f"【資料】\n")
        # f.write("・ \n")
        # f.write("\n")
        # f.write(f"【決定事項】 \n")
        # f.write("\n")
        # f.write(f"【TODO】 \n")
        # f.write("\n")
        # f.write(f"【主な議事事項】 \n")

        f.write(f"## 会議の要約 \n")
        list_formated_summary = _summary_format(texts=list_summary[-1])
        for i, doc in enumerate(list_formated_summary):
            f.write(doc)
        f.write("\n")
        f.write(f"## 会議の概要 \n")
        text_summary = "".join(list_summary[:-1])
        list_formated_summary = _summary_format(texts=text_summary)
        for i, doc in enumerate(list_formated_summary):
            f.write(doc)
        f.write("\n")
        f.write("\n")

        f.write(f"## 会議の流れ \n")
        for text, speaker in list_transcript:
            f.write("- [" + speaker + "さん]" + " \n")
            f.write("\n" + text + " \n")


def _get_list_speaker(df: pd.DataFrame) -> list:
    list_speaker = sorted(df["speaker"].unique())
    return list_speaker


def _get_list_summary(df: pd.DataFrame) -> list:
    return df["text"].to_list()


def _get_list_transcript(df: pd.DataFrame) -> list:
    """時系列に沿って話者ごとに文章をまとめる"""
    key_text: str = "text"
    key_speaker: str = "speaker"
    list_text_speaker = []
    texts = ""
    pre_speaker = df.at[0, key_speaker]
    for text, speaker in df[[key_text, key_speaker]].values:
        if pre_speaker == speaker:
            texts += str(text)
        else:
            list_text_speaker.append([texts, pre_speaker])
            pre_speaker = speaker
            texts = text
    list_text_speaker.append([texts, pre_speaker])
    return list_text_speaker


def _summary_format(texts: str):
    sents = texts.split("。")
    list_text = []
    last_num = len(sents) - 1
    for s_num, s in enumerate(sents):
        if s_num == last_num:
            list_text.append(s + "\n")
        else:
            list_text.append(s + "。" + "\n")

    return list_text


if __name__ == "__main__":
    main()
