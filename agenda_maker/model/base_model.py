from abc import ABC, abstractmethod
from typing import ClassVar

import torch

from agenda_maker.common.config_manager import ConfigManager


class BaseModel(ABC):
    def __init__(self, config_manager: ConfigManager, *args, **kwargs) -> None:
        self.config_manager = config_manager
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    model_name: ClassVar[str]

    @abstractmethod
    def set_params(self, *args, **kwargs) -> None:
        """パラメータの設定を行う"""
        raise NotImplementedError

    @abstractmethod
    def build_model(self, *args, **kwargs) -> None:
        """モデルの読み込みを行う"""
        raise NotImplementedError

    @abstractmethod
    def get_result(self, *args, **kwargs) -> None:
        """結果を取得する"""
        raise NotImplementedError
