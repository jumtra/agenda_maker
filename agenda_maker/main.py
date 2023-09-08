from pathlib import Path

from agenda_maker.agenda_logic.preprocess import preprocess
from agenda_maker.common import ConfigManager, add_log_handler, script_run


def make_agenda(
    path_input: str = "sample_data/sample.mp4", config_path: str = "agenda_maker/config/config.yaml", output_name: str = "test"
):
    """GPU Memを完全にkillするためにscript_runでscriptを随時実行"""
    # loggerの設定
    logging = add_log_handler(output_dir="./")

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

    # 親パスの取得
    parent_path = Path(__file__).resolve().parent

    logging.info(f"config_file = {config_path}")
    logging.info("<処理開始>")
    logging.info("文字起こし開始")
    # transcription
    if config_manager.config.tasks.is_transcript:
        # preprocess
        logging.info("入力データの変換前処理開始")
        path_input = preprocess(path_input=path_input, config_manager=config_manager)
        logging.info("入力データの変換前処理終了")
        script_run(
            script=str((parent_path / "agenda_logic/transcript.py").absolute()),
            cmd=["--config_path", config_path, "--input", path_input, "--output_name", output_name],
        )
    logging.info("文字起こし終了")
    # segmentation
    logging.info("文章の段落分割開始")
    if config_manager.config.tasks.is_segmentate:
        script_run(
            script=str((parent_path / "agenda_logic/segmentate.py").absolute()),
            cmd=["--config_path", config_path, "--output_name", output_name],
        )
    logging.info("文章の段落分割終了")

    # summarization
    logging.info("文章の要約開始")
    if config_manager.config.tasks.is_summarize:
        script_run(
            script=str((parent_path / "agenda_logic/summarize.py").absolute()),
            cmd=["--config_path", config_path, "--output_name", output_name],
        )
    logging.info("文章の要約終了")

    # make agenda
    logging.info("議事録の生成開始")
    script_run(
        script=str((parent_path / "agenda_logic/agenda.py").absolute()),
        cmd=["--config_path", config_path, "--output_name", output_name],
    )
    logging.info("議事録の生成終了")
    logging.info("<処理終了>")


if __name__ == "__main__":
    make_agenda()
