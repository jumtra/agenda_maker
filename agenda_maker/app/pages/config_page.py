from pathlib import Path

import gradio as gr
from omegaconf import OmegaConf

# コンフィグファイルの読み込み
config_data = OmegaConf.load(Path("agenda_maker/config/config.yaml").resolve())

# 共通のパラメータセクションを設定
common_params = gr.Interface(
    [gr.inputs.Slider(0, 100, default=config_data["common"]["seed"], label="Seed")],
    "label",
    outputs=[],
    title="Common Parameters",
    live=True,
    enable_queue=True,
)

# タスク設定ページを設定
tasks_params = gr.Interface(
    [
        gr.inputs.Checkbox(default=config_data["tasks"]["is_wav_preprocess"], label="WAV Preprocess"),
        gr.inputs.Checkbox(default=config_data["tasks"]["is_transcript"], label="Transcript"),
        gr.inputs.Checkbox(default=config_data["tasks"]["is_segmentate"], label="Segmentate"),
        gr.inputs.Checkbox(default=config_data["tasks"]["is_summarize"], label="Summarize"),
    ],
    "label",
    title="Task Settings",
    live=True,
    enable_queue=True,
)

# Preprocess設定ページを設定
preprocess_params = gr.Interface(
    [
        gr.Interface(
            [
                gr.inputs.Slider(0, 10, default=config_data["preprocess"]["cut_time"]["start_time"], label="Start Time"),
                gr.inputs.Slider(0, 10, default=config_data["preprocess"]["cut_time"]["end_time"], label="End Time"),
            ],
            "label",
            title="Cut Time",
            live=True,
            enable_queue=True,
        ),
        gr.Interface(
            [
                gr.inputs.Slider(
                    0, 1000, default=config_data["preprocess"]["silence_cut"]["min_silence_len"], label="Min Silence Length"
                ),
                gr.inputs.Slider(
                    -100, 0, default=config_data["preprocess"]["silence_cut"]["silence_thresh"], label="Silence Threshold"
                ),
                gr.inputs.Slider(0, 1000, default=config_data["preprocess"]["silence_cut"]["keep_silence"], label="Keep Silence"),
            ],
            "label",
            title="Silence Cut",
            live=True,
            enable_queue=True,
        ),
    ],
    "label",
    title="Preprocess Settings",
    live=True,
    enable_queue=True,
)

# Model設定ページを設定
model_params = gr.Interface(
    [
        gr.Interface(
            [
                gr.inputs.Slider(
                    0,
                    1,
                    default=config_data["model"]["segmentation"]["semantic_segmentation"]["threshold"],
                    label="Semantic Segmentation Threshold",
                ),
            ],
            "label",
            title="Segmentation Settings",
            live=True,
            enable_queue=True,
        ),
        gr.Interface(
            [
                gr.inputs.Checkbox(default=config_data["model"]["summarization"]["is_gpu_compile"], label="Use GPU Compile"),
                gr.inputs.Slider(0, 5000, default=config_data["model"]["summarization"]["n_ctx"], label="n_ctx"),
                gr.inputs.Slider(0, 5000, default=config_data["model"]["summarization"]["n_gpu_layers"], label="n_gpu_layers"),
                gr.inputs.Slider(
                    0, 1, default=config_data["model"]["summarization"]["params"]["temperature"], label="Temperature"
                ),
                gr.inputs.Slider(0, 1, default=config_data["model"]["summarization"]["params"]["top_p"], label="Top P"),
                gr.inputs.Slider(0, 100, default=config_data["model"]["summarization"]["params"]["top_k"], label="Top K"),
                gr.inputs.Slider(
                    0, 10, default=config_data["model"]["summarization"]["params"]["repeat_penalty"], label="Repeat Penalty"
                ),
                gr.inputs.Slider(
                    0, 5000, default=config_data["model"]["summarization"]["params"]["max_tokens"], label="Max Tokens"
                ),
            ],
            "label",
            title="Summarization Settings",
            live=True,
            enable_queue=True,
        ),
        gr.Interface(
            [
                gr.inputs.Textbox(default=config_data["model"]["whisperx"]["whisper"]["compute_type"], label="Compute Type"),
                gr.inputs.Slider(0, 10, default=config_data["model"]["whisperx"]["whisper"]["batch_size"], label="Batch Size"),
                gr.inputs.Slider(
                    0, 10, default=config_data["model"]["whisperx"]["diarization"]["min_speakers"], label="Min Speakers"
                ),
                gr.inputs.Slider(
                    0, 10, default=config_data["model"]["whisperx"]["diarization"]["max_speakers"], label="Max Speakers"
                ),
            ],
            "label",
            title="Whisperx Settings",
            live=True,
            enable_queue=True,
        ),
    ],
    "label",
    title="Model Settings",
    live=True,
    enable_queue=True,
)

model_params.launch(share=False)
