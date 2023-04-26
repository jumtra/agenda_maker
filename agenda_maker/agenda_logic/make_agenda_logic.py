import locale
from datetime import datetime

import pandas as pd

from agenda_maker.data_object.schema import AnnotateSchema, TranscriptSchema

def make_agenda(
    df_summary: pd.DataFrame,
    df_transcript_with_annotate: pd.DataFrame,
    file_name: str,
) -> None:
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().strftime("%a")
    list_speaker = _get_list_speaker(df=df_transcript_with_annotate)
    list_summary = _get_list_summary(df=df_summary)
    list_transcript = _get_list_transcript(df=df_transcript_with_annotate)
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
    with open(f"{file_name}.txt", "w") as f:
        f.write("【議事名】:xxxxx \n")
        f.write(f"【日　時】{today} ({weekday}) \n")
        f.write(f"【場　所】Meet (Web Meeting) \n")
        f.write(f"【出席者（敬称略）】\n")

        for speaker in list_speaker:
            f.write(f"・{speaker}様 \n")
        # f.write("\n")
        # f.write(f"【資料】\n")
        # f.write("・ \n")
        # f.write("\n")
        # f.write(f"【決定事項】 \n")
        # f.write("\n")
        # f.write(f"【TODO】 \n")
        # f.write("\n")
        # f.write(f"【主な議事事項】 \n")

        for num_model, text_summary in enumerate(list_summary):
            f.write(f"【要約】パターン{num_model} \n")
            list_formated_summary = _summary_format(texts=text_summary)
            for doc in list_formated_summary:
                f.write(doc)
            f.write("\n")
        f.write("\n")

        f.write(f"【会議の流れ】 \n")
        for text, speaker in list_transcript:
            f.write("[" + speaker + "さん]" + " \n")
            f.write(text + " \n")


def _get_list_speaker(df: pd.DataFrame) -> list:
    list_speaker = sorted(df[AnnotateSchema.speaker].unique())
    return list_speaker


def _get_list_summary(df: pd.DataFrame) -> list:
    return list(df.reset_index(drop=True).values.flatten())


def _get_list_transcript(df: pd.DataFrame) -> list:
    """時系列に沿って話者ごとに文章をまとめる"""
    list_text_speaker = []
    texts = ""
    pre_speaker = df.at[0, TranscriptSchema.speaker]
    for text, speaker in df[[TranscriptSchema.text, TranscriptSchema.speaker]].values:
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
    for s in sents:
        list_text.append(s + "\n")
    return list_text
