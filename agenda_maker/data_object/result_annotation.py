from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd


@dataclass
class ResultAnnotation:
    """
    Annotationの結果を保存するデータクラス
    model_name: 使用したモデルの名前
    result_str: str型の結果
    result_list: result_strを\nでsplitしたもの
    """

    model_name: str
    result_str: str
    list_result: list
    list_speaker: Optional[List[str]] = None
    list_start_time: Optional[List[float]] = None
    list_end_time: Optional[List[float]] = None
    df_result: Optional[pd.DataFrame] = None

    def time2float(self, time_str: str) -> float:
        return np.sum(
            np.array([float(x) for x in time_str.split(":")]) * np.array([360, 60, 1])
        )

    def __post_init__(self) -> None:

        self.list_speaker = list(map(lambda x: x.split(" ")[6], self.list_result))
        self.list_start_time = list(
            map(
                lambda x: self.time2float(x.split(" ")[1]),
                self.list_result,
            )
        )
        # NOTE: "]"残るから[:-1]
        self.list_end_time = list(
            map(
                lambda x: self.time2float(x.split(" ")[4][:-1]),
                self.list_result,
            )
        )
        self.df_result = pd.DataFrame(
            {
                "start_time": self.list_start_time,
                "end_time": self.list_end_time,
                "speaker": self.list_speaker,
            }
        )
