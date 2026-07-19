import argparse
from datetime import datetime

import pandas as pd

from agenda_maker.common import add_stage_arguments, load_stage_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_stage_arguments(parser, default_output_name="result")
    args = parser.parse_args()

    config_manager = load_stage_config(args.config_path, args.output_name)
    df_summarized = pd.read_csv(config_manager.config.output.path_summarized_file)
    df_whisperx = pd.read_csv(config_manager.config.output.path_whisperx_file)
    write_agenda_markdown(
        df_summarized=df_summarized,
        df_whisperx=df_whisperx,
        file_name=config_manager.config.output.path_agenda_file,
    )


def write_agenda_markdown(
    df_summarized: pd.DataFrame,
    df_whisperx: pd.DataFrame,
    file_name: str,
) -> None:
    """議事録のフォーマットに修正して書き出す。"""
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().strftime("%a")
    _agenda_format(
        file_name=file_name,
        today=today,
        weekday=weekday,
        list_speaker=_get_list_speaker(df=df_whisperx),
        list_summary=_get_list_summary(df=df_summarized),
        list_transcript=_get_list_transcript(df=df_whisperx),
    )


# 後方互換
format2agenda = write_agenda_markdown


def _agenda_format(
    file_name: str,
    today: str,
    weekday: str,
    list_speaker: list[str],
    list_summary: list[str],
    list_transcript: list[tuple[str, str]],
) -> None:
    with open(f"{file_name}.md", "w") as f:
        f.write("## 基本情報\n")
        f.write("【議事名】\txxxxx \n")
        f.write(f"\n【日　時】\t{today} ({weekday}) \n")
        f.write("\n【場　所】\tMeet (Web Meeting) \n")
        f.write("\n【出席者（敬称略）】\n")

        for speaker in list_speaker:
            f.write(f"- {speaker}様 \n")

        f.write("## 会議の要約 \n")
        for doc in _summary_format(texts=list_summary[-1]):
            f.write(doc)
        f.write("\n")
        f.write("## 会議の概要 \n")
        text_summary = "".join(list_summary[:-1])
        for doc in _summary_format(texts=text_summary):
            f.write(doc)
        f.write("\n")
        f.write("\n")

        f.write("## 会議の流れ \n")
        for text, speaker in list_transcript:
            f.write("- [" + speaker + "さん]" + " \n")
            f.write("\n" + text + " \n")


def _get_list_speaker(df: pd.DataFrame) -> list[str]:
    return sorted(df["speaker"].unique())


def _get_list_summary(df: pd.DataFrame) -> list[str]:
    return df["text"].to_list()


def _get_list_transcript(df: pd.DataFrame) -> list[tuple[str, str]]:
    """時系列に沿って話者ごとに文章をまとめる"""
    key_text = "text"
    key_speaker = "speaker"
    list_text_speaker: list[tuple[str, str]] = []
    texts = ""
    pre_speaker = df.at[0, key_speaker]
    for text, speaker in df[[key_text, key_speaker]].values:
        if pre_speaker == speaker:
            texts += str(text)
        else:
            list_text_speaker.append((texts, pre_speaker))
            pre_speaker = speaker
            texts = text
    list_text_speaker.append((texts, pre_speaker))
    return list_text_speaker


def _summary_format(texts: str) -> list[str]:
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
