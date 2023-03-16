import logging
import re
from functools import reduce
from pathlib import Path
from typing import List

import pandas as pd

from agenda_maker.common.config_manager import ConfigManager
from agenda_maker.model.base_model import BaseModel

logger = logging.getLogger()


def segmentation_logic(
    list_use_models: List[BaseModel],
    list_text: List[str],
    is_segmentation: bool,
    config_manager: ConfigManager,
    path_output: str = None,
):
    """list_use_modelsの順番にsegmentation"""

    def _is_split(list_text: list) -> bool:
        for text in list_text:
            if len(text) >= config_manager.config.model.segmentation.max_segmented_text:
                return True
            else:
                continue
        return False

    def _is_break(list_text: list) -> bool:
        return True if len(list_text) < 2 else False

    if is_segmentation and (
        len(reduce(lambda a, b: a + b, list_text))
        > config_manager.config.model.segmentation.max_segmented_text
    ):
        for model in list_use_models:
            logging.info(f"{model}を用いた文章分割開始")
            model = model(config_manager)
            model.build_model()
            list_text = model.get_result(list_text=list_text)
            if _is_split(list_text):
                # TODO: 大きい章は分解する

                pass
            if _is_break(list_text):
                pass
                # TODO: 何かしら処理の必要性
            logging.info(f"段落数：{len(list_text)}")
            logging.info(f"{model}を用いた文章分割終了")

        pd.DataFrame(list_text, columns=["text"]).to_csv(path_output, index=False)
    elif not is_segmentation:
        logging.info(f"文章分割skip")
        list_text = pd.read_csv(Path(path_output))["text"].to_list()
    else:
        logging.info(f"文章分割する必要がありません")
        return list_text
    return list_text


def annotate_logic(
    list_use_models: List[BaseModel],
    path_input: str,
    is_task: bool,
    config_manager: ConfigManager,
    path_output: str = None,
) -> pd.DataFrame:
    """list_use_modelsの順番にdf_resultを返す"""

    if is_task:
        for model in list_use_models:
            logging.info(f"{model}を用いた話者分離開始")
            model = model(config_manager)
            model.build_model()
            result = model.get_result(path_input)
            df_result = result.df_result
            df_result.to_csv(Path(path_output), index=False)
            logging.info(f"{model}を用いた話者分離終了")

    else:
        df_result = pd.read_csv(Path(path_output))

    return df_result


def transcript_logic(
    list_use_models: List[BaseModel],
    path_input: str,
    is_task: bool,
    config_manager: ConfigManager,
    path_output: str = None,
    file_name: str = None,
    is_translate: bool = False,
) -> pd.DataFrame:
    """list_use_modelsの順番にdf_resultを返す"""

    if is_task:
        for model in list_use_models:
            logging.info(f"{model}を用いて文字起こし開始")
            model = model(config_manager)
            model.build_model()
            result = model.get_result(path_input, is_translate)
            df_result = result.df_result
            df_result.to_csv(Path(path_output) / (file_name + ".csv"), index=False)
            result.df_original.to_csv(
                Path(path_output) / (file_name + "_original.csv"), index=False
            )
            logging.info(f"{model}を用いた文字起こし終了")

    else:
        df_result = pd.read_csv(Path(path_output) / (file_name + ".csv"))

    return df_result


def summarize_logic(
    list_use_models: List[BaseModel],
    list_text: List[str],
    is_task: bool,
    config_manager: ConfigManager,
    path_output: str = None,
) -> pd.DataFrame:
    """list_use_modelsの順番にsegmentation"""

    if is_task:
        dict_result = {}
        for model in list_use_models:
            logging.info(f"{model}を用いた要約開始")
            model = model(config_manager)
            model.build_model()
            dict_result[model.model_name] = model.get_result(list_text=list_text)
            logging.info(f"{model}を用いた要約終了")
        df_result = pd.DataFrame(dict_result)
        df_result.to_csv(Path(path_output), index=False)

    else:
        df_result = pd.read_csv(Path(path_output))

    return df_result


def translate_logic(
    list_use_models: List[BaseModel],
    df_summary: pd.DataFrame,
    is_task: bool,
    config_manager: ConfigManager,
    path_output: str = None,
) -> pd.DataFrame:
    """list_use_modelsの順番にsegmentation"""

    if is_task:
        dict_result = {}
        for model in list_use_models:
            logging.info(f"{model}を用いた翻訳開始")
            model = model(config_manager)
            model.build_model()
            list_translated = []
            for model_summarize in df_summary.columns:
                list_translated_summary = model.get_result(
                    list_text=df_summary[model_summarize].to_list()
                )
                list_translated.append(
                    reduce(lambda a, b: a + b, list_translated_summary)
                )
            dict_result[model.model_name] = list_translated
            logging.info(f"{model}を用いた翻訳終了")
        df_result = pd.DataFrame(dict_result, index=df_summary.columns)
        df_result.to_csv(Path(path_output))

    else:
        df_result = pd.read_csv(Path(path_output), index_col=0)

    return df_result


# ルールベースセグメンテーション
# TODO 改修する
def get_list_text(df_doc_eng: pd.DataFrame, th_max: int = 600, use_pre_text: int = 2):
    df_doc_eng["is_sep"] = df_doc_eng["text"].map(
        lambda x: True if re.match(r".*[A-Za-z0-9][.]{1}$", str(x)) != None else False
    )
    df_doc_eng["len_sentence"] = df_doc_eng["text"].map(lambda x: len(x))
    df_doc_eng = df_doc_eng.query("len_sentence >= 20")
    df_doc_eng["cumsum"] = df_doc_eng["len_sentence"].cumsum()

    sum_all_text = df_doc_eng["len_sentence"].sum()
    if sum_all_text <= th_max:
        list_text = [reduce(lambda a, b: a + b, df_doc_eng["text"].to_list())]
    else:
        list_text = []
        sum_len = 0
        list_temp = []
        for doc in df_doc_eng.values:
            text = doc[2]
            len_sentence = doc[5]
            is_sep = doc[4]
            sum_len += len_sentence
            if sum_len >= th_max and is_sep:
                list_temp.append(text)
                use_text = reduce(lambda a, b: a + b, list_temp[-use_pre_text:])
                list_temp = reduce(lambda a, b: a + b, list_temp)
                list_text.append(list_temp)
                list_temp = [use_text]
                sum_len = len(use_text)
            elif sum_len >= th_max and not is_sep:
                use_text = reduce(lambda a, b: a + b, list_temp[-use_pre_text:])
                list_temp = reduce(lambda a, b: a + b, list_temp)
                list_text.append(list_temp)
                list_temp = [use_text + text]
                sum_len = len_sentence + len(use_text)
            else:
                list_temp.append(text)
        if len(list_text) < th_max:
            df_doc_eng["cumsum"] = df_doc_eng["cumsum"] - sum_all_text + th_max

            df_temp = df_doc_eng.query("cumsum >= 0")
            list_temp = reduce(lambda a, b: a + b, df_temp["text"].to_list())
            list_text.append(list_temp)
        else:
            list_text.append(list_temp)

    return list_text
