from pathlib import Path

from agenda_maker.agenda_logic.make_agenda_logic import format2agenda
from agenda_maker.agenda_logic.segmentation import segmentation_logic
from agenda_maker.common.config_manager import ConfigManager
from agenda_maker.common.log_handler import add_log_handler
from agenda_maker.data.io import any2wav


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
    # 入力データをwav形式に変換
    logging.info("入力データの変換前処理開始")
    path_wav_input = any2wav(path_input=path_input, path_out=path_output, config_manager=config_manager)
    logging.info("入力データの変換前処理終了")

    # segmentation
    logging.info("文章の段落分割開始")
    segmentation_logic(list_text=list_text, config_manager=config_manager)
    logging.info("文章の段落分割終了")

    # summarization
    logging.info("文章の要約開始")
    logging.info("文章の要約終了")

    # make agenda
    logging.info("議事録の生成開始")
    format2agenda(
        file_name=Path(path_output) / "agenda",
        df_summary=df_translated,
        df_transcript_with_annotate=df_transcript_with_speaker,
    )
    logging.info("議事録の生成終了")
    logging.info("処理終了")


if __name__ == "__main__":
    make_agenda()
