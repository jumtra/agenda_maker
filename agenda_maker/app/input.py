import gradio as gr


def get_upload_component():
    return gr.File(label="Upload Audio/Video [wav,mp3,mp4]")
