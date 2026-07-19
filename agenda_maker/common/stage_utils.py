from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agenda_maker.common.config_manager import ConfigManager

__all__ = [
    "DEFAULT_CONFIG_PATH",
    "add_stage_arguments",
    "load_stage_config",
]

DEFAULT_CONFIG_PATH = "agenda_maker/config/config.yaml"


def add_stage_arguments(
    parser: argparse.ArgumentParser,
    *,
    require_input: bool = False,
    default_output_name: str | None = "result",
) -> argparse.ArgumentParser:
    """各パイプラインステージ共通のCLI引数を追加する。"""
    parser.add_argument("-config", "--config_path", default=DEFAULT_CONFIG_PATH, type=str)
    parser.add_argument("-output", "--output_name", default=default_output_name, type=str)
    if require_input:
        parser.add_argument("-input", "--input_path", default="sample_data/sample.mp4", type=str)
    return parser


def load_stage_config(config_path: str, output_name: str | None = None) -> ConfigManager:
    """設定を読み込み、必要なら出力ディレクトリを準備する。"""
    from agenda_maker.common.config_manager import ConfigManager

    config_manager = ConfigManager.from_path(config_path)
    if output_name is not None:
        config_manager.config.output.output_dir = str(Path(config_manager.config.output.output_dir_base) / output_name)
        Path(config_manager.config.output.output_dir).mkdir(exist_ok=True, parents=True)
    return config_manager
