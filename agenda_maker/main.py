from pathlib import Path

from agenda_maker.agenda_logic.preprocess import preprocess
from agenda_maker.common import ConfigManager, DEFAULT_CONFIG_PATH, add_log_handler, script_run


def make_agenda(
    path_input: str = "sample_data/sample.mp4",
    config_path: str = DEFAULT_CONFIG_PATH,
    output_name: str = "result",
) -> None:
    """GPU Memを完全にkillするためにscript_runでscriptを随時実行"""
    logging = add_log_handler(output_dir="./")

    if not path_input:
        message = "-inまたは--input CLIで入力ファイルのパスを指定してください"
        logging.error(message)
        raise ValueError(message)

    config_manager = ConfigManager.from_path(config_path)
    parent_path = Path(__file__).resolve().parent
    common_cmd = ["--config_path", config_path, "--output_name", output_name]

    logging.info(f"config_file = {config_path}")
    logging.info("<処理開始>")

    stages = [
        ("文字起こし", "is_transcript", "agenda_logic/transcript.py", True),
        ("文章の段落分割", "is_segmentate", "agenda_logic/segmentate.py", False),
        ("文章の要約", "is_summarize", "agenda_logic/summarize.py", False),
        ("議事録の生成", None, "agenda_logic/agenda.py", False),
    ]

    for label, task_flag, script_name, needs_preprocess in stages:
        enabled = True if task_flag is None else bool(getattr(config_manager.config.tasks, task_flag))
        logging.info(f"{label}開始")
        if enabled:
            cmd = list(common_cmd)
            if needs_preprocess:
                logging.info("入力データの変換前処理開始")
                path_input = preprocess(path_input=path_input, config_manager=config_manager)
                logging.info("入力データの変換前処理終了")
                cmd.extend(["--input", path_input])
            script_run(
                script=str((parent_path / script_name).absolute()),
                cmd=cmd,
            )
        logging.info(f"{label}終了")

    logging.info("<処理終了>")


if __name__ == "__main__":
    make_agenda()
