# 議事録生成AI

動画や音声データを入力として、文字起こし、話者割り当てと要約の結果を出力します。

## 概要
このプロジェクトは、音声・動画データから議事録を自動生成するためのライブラリです。具体的には、音声データから文字起こし、話者割り当て、テキストセグメンテーション、要約を行い、最終的には生成された議事録を出力します。

## 特徴

* 文字起こし：Whisperと呼ばれる音声認識技術を使用して、音声データからテキストへの変換を行います。
* 話者割り当て：Pyannoteというライブラリを使用して、音声データから話者を自動的に分離します。
* テキストセグメンテーション：TextTillingやSentenceTransformerを使用して、テキストを段落に分割します。
* 要約：LLama2 ELYZAを使用して、生成されたテキストを要約します。
* 文書校正：LLama2 ELYZAを使用して、生成されたテキストを文章校正します。

## 使い方
#### 実行方法
基本的にpath_inputにwav,mp3,mp4形式のデータのパスを渡すことで議事録の生成が可能です。

* コマンドラインで実行する場合
  - agenda path_input = "入力ファイルのパス"
  - path_output="出力先のパス" 
  - config_path = "パラメーター各種のyamlファイルのパス"

## 実行環境

- OS: Ubuntu20.04
- CPU: Rythen7 3700X
- GPU: GEFORCE RTX2070 SUPER(8GB)
- MEMORY: 32GB

## 環境構築


### Dockerを使う場合
make, dockerが必要です。

* make version

```
GNU Make 4.2.1
Built for x86_64-pc-linux-gnu
Copyright (C) 1988-2016 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

* docker version
```
Docker version 24.0.5, build ced0996
```

#### 1. HF_TOKENの設定

.env内にHF_TOKENを入力してください。

```.env
HF_TOKEN =hf_xxxx
```

#### 2. モデルのダウンロード
以下のコマンドでモデルをダウンロード

```
make prepare
```

#### 3. コンテナビルド
以下のコマンドでモデルをダウンロード

```
make start
```

#### 4. コンテナクローズ
以下のコマンドでdockerを終了してキャッシュを削除
```
make stop
make clear
```

### ローカルで環境構築する場合
#### 1. 事前準備
* Python 3.10のインストール
本ライブラリはPython 3.10系でのみ実行確認をしています。

* FFmpegのインストール
Whisperxの使用や音声データの加工をするために必要です。

* Hugging Faceアカウント
各種モデルをHugging Face Hubからインストールするために使用します。ログインできれば問題ありません。

**HF_TOKEN**を取得するために使用します。
#### 2. 必要なライブラリのインストール
以下のコマンドでpoetry.lockから依存関係をインストール
```
poetry config installer.max-workers 10
poetry install --no-interaction --no-ansi -vvv
```
* llama-cpp-pythonのインストール
  - CPUを使う場合

  ```
  CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" FORCE_CMAKE=1 pip install llama-cpp-python==0.1.83 --no-cache-dir
  ```
  - GPUを使う場合

  ```
  CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 python3 -m pip install llama-cpp-python==0.1.83 --no-cache-dir
  ```
## 実行方法

以下のコマンドで実行可能

```
python agenda_maker/cli.py
```

引数は、以下のものを使用
```
options:
  -h, --help            show this help message and exit
  -config CONFIG_PATH, --config_path CONFIG_PATH
  -input INPUT_PATH, --input_path INPUT_PATH(mp3 or mp4 or wav)
  -output OUTPUT_NAME, --output_name OUTPUT_NAME
```
## コンフィグの設定

| パラメータ                           | 説明                                                                                                  |
|----------------------------------|-------------------------------------------------------------------------------------------------------|
| **tasks**                         | 実行するタスク設定                                                                                      |
| is_wav_preprocess                | True: WAV前処理を実行する、False: 実行しない                                                       |
| is_transcript                    | True: テキスト変換を実行する、False: 実行しない                                                      |
| is_segmentate                    | True: セグメンテーションを実行する、False: 実行しない                                                 |
| is_summarize                     | True: 要約を実行する、False: 実行しない                                                              |
| **common**                        | 共通部分のパラメータ                                                                                     |
| seed                             | 乱数生成のシード値                                                                                     |
| **output**                        | 出力設定                                                                                              |
| output_dir_base                  | ベースの出力ディレクトリ名                                                                               |
| output_dir                       | 出力ディレクトリの詳細な設定（以下のファイルの出力ディレクトリを指定）                                    |
| path_segmented_file              | セグメンテーション結果のCSVファイルの出力パス                                                         |
| path_summarized_file             | 要約結果のCSVファイルの出力パス                                                                       |
| path_whisperx_file               | Whisperx結果のCSVファイルの出力パス                                                                   |
| path_seg_word_file               | セグメンテーションされた単語のCSVファイルの出力パス                                                    |
| path_agenda_file                 | アジェンダファイルの出力パス                                                                           |
| **preprocess**                    | プリプロセス設定                                                                                       |
| cut_time                         | 音声データのカット設定                                                                                 |
| start_time                       | 音声データの初めてn秒をカット                                                                         |
| end_time                         | 音声データの終わりn秒をカット                                                                         |
| silence_cut                      | 無音のカット設定                                                                                      |
| min_silence_len                  | n秒以上無音なら分割                                                                                   |
| silence_thresh                   | ndBFS以下で無音と判定                                                                                  |
| keep_silence                     | 分割後Nmsは無音を残す                                                                                 |
| **model**                         | モデル設定                                                                                             |
| **segmentation**                  | 文章分割のパラメータ                                                                                    |
| max_segment_text                 | 1セグメントの最大文字数                                                                               |
| min_segment_text                 | 1セグメントの最小文字数                                                                               |
| max_segment_num                  | 最大セグメント数                                                                                       |
| min_segment_num                  | 最小セグメント数                                                                                       |
| semantic_segmentation            | セマンティックセグメンテーションの設定                                                                |
| model_type                       | SentenceTransformerのモデルタイプ                                                                       |
| threshold_step                   | 閾値ステップ設定                                                                                        |
| threshold                        | 閾値設定                                                                                              |
| texttiling                       | テキストティリングのパラメータ                                                                         |
| w                                | 擬似文のサイズ                                                                                         |
| k                                | ブロック比較法で使用されるブロックのサイズ                                                             |
| summarization                    | 要約のパラメータ                                                                                        |
| model_path                       | 要約モデルのパス                                                                                        |
| is_gpu_compile                   | llama.cppでcublasを使用するかどうかの設定                                                              |
| n_ctx                            | コンテキストサイズ                                                                                     |
| n_gpu_layers                     | GPUレイヤー数                                                                                          |
| params                           | 要約のパラメータ                                                                                        |
| temperature                      | 温度設定                                                                                              |
| top_p                            | Top-pサンプリングの閾値設定                                                                           |
| top_k                            | Top-kサンプリングの閾値設定                                                                           |
| repeat_penalty                   | リピートのペナルティ設定                                                                               |
| max_tokens                       | 最大トークン数                                                                                         |
| stop                             | 停止ワードの設定                                                                                       |
| whisperx                         | Whisperx設定                                                                                          |
| whisper                          | 文字起こしのパラメータ                                                                                  |
| model_type                       | Whisperモデルのタイプ                                                                                  |
| compute_type                     | 計算タイプ（float16など）                                                                              |
| batch_size                       | バッチサイズ                                                                                            |
| diarization                      | 話者分離のパラメータ                                                                                   |
| min_speakers                     | 発話している最小人数                                                                                   |
| max_speakers                     | 発話している最大人数                                                                                   |

## 作成者

* jumtras

