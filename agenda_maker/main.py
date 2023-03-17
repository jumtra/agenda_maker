from pathlib import Path

from agenda_maker.agenda_logic.allocate_speaker_logic import allocate_speaker
from agenda_maker.agenda_logic.get_result_logic import (
    annotate_logic,
    segmentation_logic,
    summarize_logic,
    transcript_logic,
    translate_logic,
)
from agenda_maker.agenda_logic.make_agenda_logic import make_agenda
from agenda_maker.common.config_manager import ConfigManager
from agenda_maker.common.log_handler import add_log_handler
from agenda_maker.data.io import any2wav
from agenda_maker.model.get_model_class import get_model_class


def make_agenda(
    path_input: str,
    path_output: str = "./result",
    config_path: str = "agenda_maker/config/config.yaml",
):
    # loggerの設定
    logging = add_log_handler(output_dir=path_output)

    if path_input is None:
        logging.error("-inまたは--input CLIで入力ファイルのパスを指定してください")
        raise Exception("-inまたは--input CLIで入力ファイルのパスを指定してください")
    # configfile読み込む
    config_dir = str("/".join(Path(config_path).parts[:-1]))
    config_yaml_path = str(Path(config_path).parts[-1])
    config_manager = ConfigManager.from_yaml(
        config_yaml_path=config_yaml_path,
        config_dir=config_dir,
    )
    Path(path_output).mkdir(parents=True, exist_ok=True)

    logging.info(f"config_file = {config_path}")
    logging.info("処理開始")
    # 使用するモデルの選択
    dict_use_models = config_manager.config.common.use_models
    # 入力データをwav形式に変換
    logging.info("入力データの変換前処理開始")
    path_wav_input = any2wav(
        path_input=path_input, path_out=path_output, config_manager=config_manager
    )
    logging.info("入力データの変換前処理終了")

    # speaker_diarization
    logging.info("話者分離開始")
    list_annotate_models = [
        get_model_class(model) for model in dict_use_models.annotation
    ]
    df_annotate = annotate_logic(
        list_use_models=list_annotate_models,
        path_input=path_wav_input,
        path_output=path_output + "/annotation.csv",
        config_manager=config_manager,
        is_task=config_manager.config.tasks.annotation_is,
    )
    logging.info("話者分離終了")

    # transcript
    logging.info("文字起こし開始")
    list_transcript_models = [
        get_model_class(model) for model in dict_use_models.transcription
    ]
    logging.info("日本語への文字起こし開始")
    df_transcript = transcript_logic(
        list_use_models=list_transcript_models,
        path_input=path_wav_input,
        path_output=path_output,
        file_name="transcript",
        config_manager=config_manager,
        is_task=config_manager.config.tasks.transcription_is,
        is_translate=False,
    )
    logging.info("英語への文字起こし開始")
    df_eng_transcript = transcript_logic(
        list_use_models=list_transcript_models,
        path_input=path_wav_input,
        path_output=path_output,
        file_name="transcript_eng",
        config_manager=config_manager,
        is_task=config_manager.config.tasks.transcription_eng_is,
        is_translate=True,
    )
    logging.info("英語への文字起こし終了")

    # segmentation
    logging.info("文章の段落分割開始")
    list_seg_models = [get_model_class(model) for model in dict_use_models.segmentation]
    list_segmented_text = segmentation_logic(
        list_use_models=list_seg_models,
        list_text=df_eng_transcript["text"].to_list(),
        path_output=path_output + "/segmented_text.csv",
        config_manager=config_manager,
        is_segmentation=config_manager.config.tasks.segmentation_is,
    )
    logging.info("文章の段落分割終了")

    # summarization
    logging.info("文章の要約開始")
    list_sum_models = [
        get_model_class(model) for model in dict_use_models.summarization
    ]
    df_summary = summarize_logic(
        list_use_models=list_sum_models,
        list_text=list_segmented_text,
        config_manager=config_manager,
        path_output=path_output + "/summarized_text.csv",
        is_task=config_manager.config.tasks.summarization_is,
    )
    logging.info("文章の要約終了")

    # translate
    logging.info("文章の翻訳開始")
    list_translate_models = [
        get_model_class(model) for model in dict_use_models.translation
    ]
    df_translated = translate_logic(
        list_use_models=list_translate_models,
        df_summary=df_summary,
        config_manager=config_manager,
        path_output=path_output + "/translated_text.csv",
        is_task=config_manager.config.tasks.translation_is,
    )
    logging.info("文章の翻訳終了")

    # merge df_annotate and df_transcript
    df_transcript_with_speaker = allocate_speaker(
        df_annotate=df_annotate, df_transcript=df_transcript
    )
    df_transcript_with_speaker.to_csv(
        Path(path_output) / "transcript_with_speaker.csv", index=False
    )

    # make agenda
    logging.info("議事録の生成開始")
    make_agenda(
        file_name=Path(path_output) / "agenda",
        df_summary=df_translated,
        df_transcript_with_annotate=df_transcript_with_speaker,
    )
    logging.info("議事録の生成終了")
    logging.info("処理終了")


if __name__ == "__main__":
    make_agenda()
