# 議事録生成AI

動画や音声データを入力として、文字起こし、話者割り当てと要約の結果を出力します。

## 概要
このプロジェクトは、音声・動画データから議事録を自動生成するためのライブラリです。具体的には、音声データから文字起こし、話者割り当て、テキストセグメンテーション、要約を行い、最終的には生成された議事録を出力します。

## 特徴

* 文字起こし：Whisperと呼ばれる音声認識技術を使用して、音声データからテキストへの変換を行います。
* 話者割り当て：Pyannoteというライブラリを使用して、音声データから話者を自動的に分離します。
* テキストセグメンテーション：TextTillingやTransformerを使用して、テキストを段落に分割します。
* 要約：Pegasusという言語モデルを使用して、生成されたテキストを要約します。
* 翻訳：FuguMtという翻訳モデルを使用して、要約結果を翻訳します。

## 使い方
#### 実行方法
基本的にpath_inputにwav,mp3,mp4形式のデータのパスを渡すことで議事録の生成が可能です。
path_outputはデフォルトでresultディレクトリが指定されており、存在しない場合は作成して出力結果を格納します。
config_pathはconfig.yamlのパスを指定します。デフォルトでは、リポジトリ内のconfig.yamlを読み込み、モデル各種のパラメーターを設定します。独自のパラメーターを設定したい場合は事項を参考にconfig.yamlを作成してファイルのパスを渡してください。

* コマンドラインで実行する場合
```
agenda path_input = "入力ファイルのパス" path_output="出力先のパス" config_path = "パラメーター各種のyamlファイルのパス"
* preprocess: 音声データの前処理に関するパラメータを指定します。
例えば、silence_cutでは、無音部分を分割の基準として利用します。
* model: 各タスクで使用するモデルに関するパラメータを指定します。
例えば、segmentationでは、文書を分割する際に用いるSemantic SegmentationやText Tilingのパラメータが指定されています。また、summarizationでは、PegasusやPegasusXといった要約モデルのパラメータが指定されています。

config.yaml
```
# 実行するタスク設定
tasks:
  wav_preprocess_is: True
  annotation_is: True
  transcription_is: True
  transcription_eng_is: True
  segmentation_is: True
  summarization_is: True
  translation_is: True

# 共通部分のパラメータ
common:
  seed: 42
  use_models:
    annotation: [model_pyaudio]
    segmentation: [model_text_tilling,model_semantic_segmentation,model_transformer_text_classify]
    summarization: [model_pegasus,model_pegasusx]
    translation: [model_marianmt]
    transcription: [model_whisper]

preprocess:
  cut_time:
    start_time: 0
    end_time: 5
  silence_cut:
    min_silence_len: 500 #n秒以上無音なら分割
    silence_thresh: -60 #ndBFS以下で無音と判定
    keep_silence: 50 #分割後Nmsは無音を残す
  
model: 
  # 話者分離のパラメータ
  annotation:
    model_name: model_pyaudio
    min_speakers: 1
    max_speakers: 4

  # 文章分割のパラメータ
  # sementic segmentation のパラメータ
  segmentation:
    max_segmented_text: 8000
    segment_num: 4
    semantic_segmentation:
      model_name: model_semantic_segmentation
      model_type: all-MiniLM-L6-v2 # SentenceTransformerのモデルタイプ
      max_segment_text: 8000
      threshold_step: 0.01
      threshold: 0.6
    # text tillingのパラメータ
    text_tiling:
      model_name: model_text_tilling
      w: 15 #Pseudosentence size
      k: 10 #Size (in sentences) of the block used in the block comparison method
      smoothing_width: 2 #The width of the window used by the smoothing method
      smoothing_rounds: 10 #The number of smoothing passes
    # 文章類似セグメンテーションのパラメータ
    bert:
      model_name: model_transformer_text_classify
      model_type: dennlinger/bert-wiki-paragraphs
      max_segment_text: 8000
      threshold_step: 0.01
      threshold: 0.6

  # 要約のパラメータ
  summarization:
    max_summary_text: 1000
    pegasus:
      model_name: model_pegasus
      model_type: google/pegasus-large 
      tokenizer_type: google/pegasus-large 
      min_length: 50
      max_length: 1000
      use_first: False
      no_repeat_ngram_size: 3
      num_beams: 10
    pegasus_x:
      model_name: model_pegasusx
      model_type: google/pegasus-x-large 
      tokenizer_type: google/pegasus-x-large 
      min_length: 50
      max_length: 1000
      use_first: False
      no_repeat_ngram_size: 3
      num_beams: 10
  # 翻訳のパラメータ
  translation:
    marian:
      model_name: model_marianmt
      model_type: staka/fugumt-en-ja
      tokenizer_type: staka/fugumt-en-ja
      max_length: 1100
      no_repeat_ngram_size: 3
      num_beams: 10
      input_max_length: 1100

  # 文字起こしのパラメータ
  transcription:
    engwords_per_line: 20 # 英語データフレーム上の最小文字数
    jpwords_per_line: 10 # 日本語データフレーム上の最小文字数
    whisper:
      model_name: model_whisper
      model_type: large-v2
      verbose: False
      condition_on_previous_text: True # default True
      logprob_threshold: -1.0
      no_speech_threshold: 0.6
```

## インストール
#### 1. 事前準備
* Python 3.8のインストール
本ライブラリはPython 3.8系でのみ実行確認をしています。

* FFmpegのインストール
Whisperの使用や音声データの加工をするために必要です。

* Hugging Faceアカウント
各種モデルをHugging Face Hubからインストールするために使用します。ログインできれば問題ありません。
#### 2. 必要なライブラリのインストール
* torch1.2.1+cuxxのインストール
cudaとtorchのバージョンが合わないため再インストールを行ってください。

poetryを利用する場合は以下の手順を参考にインストールしてください。
```
pyproject.toml[tool.poetry.dependencies]に以下を追加

torch = {url ="https://download.pytorch.org/whl/cu113/torch-1.12.0%2Bcu113-cp38-cp38-linux_x86_64.whl"}
torchaudio = { url = "https://download.pytorch.org/whl/cu113/torchaudio-0.12.0%2Bcu113-cp38-cp38-linux_x86_64.whl"}
torchvision = { url = "https://download.pytorch.org/whl/cu113/torchvision-0.13.0%2Bcu113-cp38-cp38-linux_x86_64.whl"}

```
```
poetry install
```


* en_core_web_smのインストール
以下のコマンドを実行

```
python -m spacy download en_core_web_sm 
```

## ライセンス

本プロジェクトで使用したモデルのライセンスは以下です。
* Pyannote
    - License：MIT licence
    - 参照：https://huggingface.co/pyannote/speaker-diarization

* Whisper
    - License：MIT licence
    - 参照：https://github.com/openai/whisper

* Pegasus
    - License：Apache License 2.0
    - 参照：https://github.com/google-research/pegasus

* FuguMT
    - License：CC BY-SA 4.0
    - 参照：https://staka.jp/wordpress/?p=413
* bert-wiki-paragraphs
    - License：MIT licence
    - 参照：https://huggingface.co/dennlinger/bert-wiki-paragraphs
## 作成者

* jumtras

## サポート

