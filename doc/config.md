# コンフィグの設定

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
| th_segment_num                  | 最大セグメント数                                                                                       |
| semantic_segmentation            | セマンティックセグメンテーションの設定                                                                |
| model_type                       | SentenceTransformerのモデルタイプ                                                                       |
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