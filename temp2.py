# ライブラリのインストール
#!CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python
# CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --no-cache-dir llama-cpp-python
##（CPUで実行する場合）!pip install llama-cpp-python
#!pip install gradio
#
## モデルのダウンロード
# wget https://huggingface.co/mmnga/ELYZA-japanese-Llama-2-7b-gguf/resolve/main/ELYZA-japanese-Llama-2-7b-q4_0.gguf
## ウェブUIの起動
import copy

import gradio as gr
from llama_cpp import Llama

llm = Llama(
    model_path="model_dir/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_0.gguf",
    n_ctx=2048,
    n_gpu_layers=100,  # CPUで実行する場合は削除
)

history = []

system_message = """
あなたはAIアシスタントです。
"""


def generate_text(message, history):
    temp = ""
    input_prompt = f"{system_message}"
    for interaction in history:
        input_prompt = input_prompt + "\nUSER: " + str(interaction[0]) + "\nASSISTANT: " + str(interaction[1])
    input_prompt = input_prompt + "\nUSER: " + str(message) + "\nASSISTANT: "

    output = llm.create_completion(
        input_prompt,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
        repeat_penalty=1.1,
        max_tokens=2048,
        stop=[
            "ASSISTANT:",
            "USER:",
            "SYSTEM:",
        ],
        stream=True,
    )
    for out in output:
        stream = copy.deepcopy(out)
        temp += stream["choices"][0]["text"]
        yield temp

    history = ["init", input_prompt]


demo = gr.ChatInterface(
    generate_text,
    title="Japanese chatbot using llama-cpp-python",
    description="",
    examples=["日本の四国にある県名を挙げてください。"],
    cache_examples=True,
    retry_btn=None,
    undo_btn="Remove last",
    clear_btn="Clear all",
)
demo.queue(concurrency_count=1, max_size=5)
demo.launch(debug=True, share=False)
