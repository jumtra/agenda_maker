import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
import spacy


@dataclass
class ResultWhisper:
    """Whisperの結果を保存するデータクラス
    engwords_per_line: 英語データフレーム上の最小文字数
    jpwords_per_line: 日本語データフレーム上の最小文字数
    is_translate: 翻訳処理のフラグ
    language: 使用言語
    transcript_text: 文字起こしされたテキスト
    list_result: whisper.transcribeの結果リスト
    """

    engwords_per_line: int
    jpwords_per_line: int
    is_translate: bool
    language: str
    transcript_text: str
    list_result: list
    df_result: Optional[pd.DataFrame] = None
    df_original: Optional[pd.DataFrame] = None

    def remove_filler_expression(self, nlp, text: str) -> str:
        """日本語形態素解析を用いたノイズ除去"""
        text = text.replace(" ", "")
        text = text.replace("　", "")

        doc = nlp(text)
        new_text = ""
        for doc_num, sent in enumerate(doc.sents):
            for token in sent:
                # フィラー感嘆詞/接頭辞削除
                if str(token.pos_) != "INTJ" and str(token.tag_) != "接頭辞":

                    # NOTE: whisperが学習データに引っ張られて知らない人の名前を
                    # 冒頭で出すことがあるから

                    # 冒頭固有名詞削除
                    if doc_num == 0 and (
                        str(token.tag_) == "名詞-固有名詞-人名-一般"
                        or str(token.tag_) == "名詞-固有名詞-人名-姓"
                        or str(token.tag_) == "名詞-固有名詞-人名-名"
                    ):
                        continue
                    else:
                        new_text += str(token)

        return new_text

    def remove_noise(self, text: str) -> str:
        """ノイズ除去"""
        text = re.sub(r"【.*】", "", text)
        text = re.sub(r"（.*）", "", text)
        text = re.sub(r"「.*」", "", text)
        text = re.sub(r"[［］\[\]]", " ", text)  # ［］の除去
        text = re.sub(r"[@＠]\w+", "", text)  # メンションの除去
        text = re.sub(r"https?:\/\/.*?[\r\n ]", "", text)  # URLの除去
        text = re.sub(r"　", " ", text)  # 全角空白の除去
        text = text.replace("\u200b", "")
        text = text.replace("おだしょー", "")
        text = text.replace("/", "")
        return text

    def remove_min_text(self, text: str, min_length: int) -> str:
        if len(text) <= min_length:
            return ""
        else:
            return text

    def remove_duplication(self, df_result: pd.DataFrame) -> pd.DataFrame:
        """文の重複を削除（繰り返して完全一致の文章があったら1つを残して削除する）"""
        return df_result.drop_duplicates(subset="text", keep="first").reset_index(
            drop=True
        )

    def remove_unicode(self, text: str, form="NFKC") -> str:
        normalized_text = unicodedata.normalize(form, text)
        return normalized_text

    def __post_init__(self) -> None:
        df_result = pd.DataFrame(self.list_result)
        self.df_original = pd.DataFrame(self.list_result)
        list_text = df_result["text"].to_list()

        # 文章が英語のときにする処理
        if self.is_translate:

            for list_id, text in enumerate(list_text):
                text = self.remove_unicode(text)
                text = self.remove_noise(text)
                text = self.remove_min_text(text, self.engwords_per_line)
                if len(text) == 0:
                    list_text[list_id] = float("nan")
                else:
                    list_text[list_id] = text

        # 文章が日本語のときにする処理
        else:
            spacy.require_gpu()
            nlp = spacy.load("ja_ginza_electra")
            for list_id, text in enumerate(list_text):
                text = self.remove_unicode(text)
                text = self.remove_noise(text)
                text = self.remove_min_text(text, self.jpwords_per_line)
                if len(text) == 0:
                    list_text[list_id] = float("nan")
                else:
                    list_text[list_id] = self.remove_filler_expression(nlp, text)
        # 文の重複を削除
        df_result.loc[:, "text"] = list_text
        df_result = self.remove_duplication(df_result)
        # 文の欠損削除
        df_result = df_result.dropna(subset="text", axis=0).reset_index(drop=True)
        self.df_result = df_result
