import numpy as np
import pandas as pd

from agenda_maker.data_object.schema import AnnotateSchema, TranscriptSchema


def allocate_speaker(
    df_annotate: pd.DataFrame, df_transcript: pd.DataFrame
) -> pd.DataFrame:
    df_transcript = _simple_allocate_speaker(
        df_annotate=df_annotate, df_transcript=df_transcript
    )
    df_transcript = _pad_none_speaker(
        df_annotate=df_annotate, df_transcript=df_transcript
    )
    df_transcript = df_transcript[[TranscriptSchema.text, TranscriptSchema.speaker]]
    return df_transcript


def _simple_allocate_speaker(
    df_annotate: pd.DataFrame, df_transcript: pd.DataFrame
) -> pd.DataFrame:
    """アノテーションの範囲に入っているtextにspeakerを割り当てる"""
    df_transcript[TranscriptSchema.speaker] = "None"
    for start, end, speaker in df_annotate.values:
        mask_label = (start <= df_transcript[TranscriptSchema.start]) & (
            df_transcript[TranscriptSchema.end] <= end
        )
        if any(mask_label):
            df_transcript.loc[mask_label, TranscriptSchema.speaker] = speaker
    return df_transcript


def _pad_none_speaker(
    df_annotate: pd.DataFrame, df_transcript: pd.DataFrame
) -> pd.DataFrame:
    """spekerが割り当てられていない文章に近いspeakerを割り当てる"""
    df_not_allocated = (
        df_transcript[
            [TranscriptSchema.start, TranscriptSchema.end, TranscriptSchema.speaker]
        ]
        .loc[df_transcript[TranscriptSchema.speaker] == "None"]
        .reset_index()
    )

    for index, start, end, _ in df_not_allocated.values:
        start_min = min(abs(start - df_annotate[AnnotateSchema.start]))
        end_min = min(abs(df_annotate[AnnotateSchema.end] - end))
        if start_min <= end_min:
            selected_index = np.argmin(abs(start - df_annotate[AnnotateSchema.start]))
        else:
            selected_index = np.argmin(abs(df_annotate[AnnotateSchema.end] - end))

        speaker = df_annotate.iloc[selected_index][AnnotateSchema.speaker]
        df_transcript.loc[int(index), TranscriptSchema.speaker] = speaker
    return df_transcript
