from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from omegaconf import DictConfig, OmegaConf

__all__ = ["ConfigManager"]


@dataclass(frozen=True)
class ConfigManager:
    """config管理クラス"""

    config: DictConfig
    config_dir: str

    @classmethod
    def from_path(cls, config_path: str | Path, enable_merge_cli_args: bool = False) -> ConfigManager:
        """yamlファイルのフルパスから読み込む。"""
        path = Path(config_path)
        return cls.from_yaml(
            config_dir=str(path.parent),
            config_yaml_path=path.name,
            enable_merge_cli_args=enable_merge_cli_args,
        )

    @classmethod
    def from_yaml(cls, config_dir: str, config_yaml_path: str, enable_merge_cli_args: bool = False) -> ConfigManager:
        """yamlファイルの読み込み
        enable_merge_cli_args: CLI引数からconfigを受け取る場合使用
        """
        yaml_config = OmegaConf.load(f"{config_dir}/{config_yaml_path}")

        if not enable_merge_cli_args:
            return cls(yaml_config, config_dir)

        cli_config = OmegaConf.from_cli()
        config = OmegaConf.merge(yaml_config, cli_config)
        return cls(config, config_dir)

    def save_yaml(self, filename: Union[str, Path]) -> None:
        """設定をyamlファイルとしてファイル出力する"""
        with open(filename, "w") as f:
            f.write(OmegaConf.to_yaml(self.config, resolve=True))
