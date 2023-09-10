import argparse
import logging
import uuid
from pathlib import Path

import gradio as gr

from agenda_maker.common import ConfigManager, zip_directory
from agenda_maker.common.config_manager import ConfigManager
from agenda_maker.main import make_agenda

logger = logging.getLogger(__file__)

ALLOWED_EXTENSIONS = {"wav", "mp3", "mp4"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def read_markdown(path_file: str | Path) -> str:
    with open(path_file, encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines)


def get_upload_component():
    return gr.File(label="Upload Audio/Video")


def generate_agenda(
    input_audio_video,
    tasks_is_wav_preprocess,
    is_gpu_compile,
    min_speakers,
    max_speakers,
    cut_time_start_time,
    cut_time_end_time,
):
    if input_audio_video is None or not allowed_file(input_audio_video.name):
        return "Invalid file format. Please upload a valid audio or video file.", None, None
    config_manager = ConfigManager.from_yaml(config_yaml_path="config.yaml", config_dir="agenda_maker/config")
    config_manager.config.tasks.is_wav_preprocess = tasks_is_wav_preprocess
    config_manager.config.model.summarization.is_gpu_compile = is_gpu_compile
    config_manager.config.model.whisperx.diarization.min_speakers = min_speakers
    config_manager.config.model.whisperx.diarization.max_speakers = max_speakers
    config_manager.config.preprocess.cut_time.start_time = cut_time_start_time
    config_manager.config.preprocess.cut_time.end_time = cut_time_end_time

    uid = uuid.uuid1()

    input_path = str(Path(input_audio_video.orig_name).resolve())
    path_root = Path(input_path).parent
    output_path = path_root / str(uid)
    (output_path).mkdir(exist_ok=True, parents=True)

    # configの設定変更
    config_manager.config.output.output_dir_base = str(path_root)
    config_manager.config.output.output_dir = str(output_path)
    config_manager.save_yaml(filename=path_root / "config.yaml")
    make_agenda(path_input=input_path, output_name=str(uid), config_path=str(path_root / "config.yaml"))
    path_zip = str(path_root / "result.zip")
    path_agenda = str(output_path / "agenda.md")
    zip_directory(directory_path=output_path, output_zip_file=path_zip)

    markdown = read_markdown(path_agenda)

    return markdown, path_agenda, path_zip


def app():
    with gr.Blocks(title="議事録AI") as demo:
        gr.Markdown("# 議事録作成AI")

        with gr.Tabs():
            # home
            with gr.TabItem("議事録生成"):
                input_audio_video = get_upload_component()
                with gr.Row():
                    output_download = gr.File(label="Download Agenda", elem_id="output_download")
                    output_zip = gr.File(label="Download All Results", elem_id="output_zip")
                with gr.Accordion(label="パラメータの設定", open=True):
                    # tasks
                    with gr.Row():
                        tasks_is_wav_preprocess = gr.Checkbox(value=True, label="音声の前処理を実行するかどうか")

                        # preprocess
                        preprocess_cut_time_start_time = gr.Slider(minimum=0, maximum=60, step=1, value=0, label="音声の序盤をカットする秒数")
                        preprocess_cut_time_end_time = gr.Slider(minimum=0, maximum=60, step=1, value=0, label="音声の終盤をカットする秒数")
                    with gr.Row():
                        # model - summarization
                        model_summarization_is_gpu_compile = gr.Checkbox(value=True, label="LLMでGPUを使うかどうか")
                        # model - whisperx
                        model_whisperx_diarization_min_speakers = gr.Slider(
                            minimum=1,
                            maximum=10,
                            step=1,
                            value=1,
                            label="会議で話した最小人数",
                        )
                        model_whisperx_diarization_max_speakers = gr.Slider(
                            minimum=1,
                            maximum=10,
                            step=1,
                            value=4,
                            label="会議で話した最大人数",
                        )

                submit_btn = gr.Button("実行", variant="primary")
            ## result
            with gr.TabItem("作成結果"):
                outputbox = gr.Markdown(label="出力", elem_id="outputbox")

            ## 説明書
            with gr.TabItem("README"):
                gr.Markdown(read_markdown(str(Path(__file__).resolve().parents[1] / "doc/app.md")))

            # Action
            submit_btn.click(
                fn=generate_agenda,
                inputs=[
                    input_audio_video,
                    tasks_is_wav_preprocess,
                    model_summarization_is_gpu_compile,
                    model_whisperx_diarization_min_speakers,
                    model_whisperx_diarization_max_speakers,
                    preprocess_cut_time_start_time,
                    preprocess_cut_time_end_time,
                ],
                outputs=[outputbox, output_download, output_zip],
            )
    return demo


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-pass", "--password", default="password", type=str)
    parser.add_argument("-id", "--user_id", default="user", type=str)
    parser.add_argument("-share", "--share", default="True", type=str)
    parser.add_argument("-inl", "--inline", default="False", type=str)
    parser.add_argument("-auth", "--is_auth", default="True", type=str)
    parser.add_argument("-queue", "--enable_queue", default="True", type=str)
    parser.add_argument("-port", "--port", default=None, type=int)
    args = parser.parse_args()
    user_id = args.user_id
    password = args.password
    share = args.share == "True"
    inline = args.inline == "True"
    is_auth = args.is_auth == "True"
    enable_queue = args.enable_queue == "True"
    port = args.port
    demo = app()
    demo.launch(
        enable_queue=enable_queue,
        inline=inline,
        max_threads=30,
        auth=(user_id, password) if is_auth else None,
        show_error=True,
        server_port=port,
        share=share,
    )


if __name__ == "__main__":
    main()
