"""共通ユーティリティ。重い依存は必要時に遅延インポートする。"""

from .script_run_kill import script_run
from .stage_utils import DEFAULT_CONFIG_PATH, add_stage_arguments, load_stage_config
from .text_cleanup import remove_text_noise

__all__ = [
    "ConfigManager",
    "DEFAULT_CONFIG_PATH",
    "add_log_handler",
    "add_stage_arguments",
    "load_stage_config",
    "release_gpu_memory",
    "remove_text_noise",
    "script_run",
    "zip_directory",
]


def __getattr__(name: str):
    if name == "ConfigManager":
        from .config_manager import ConfigManager

        return ConfigManager
    if name == "add_log_handler":
        from .log_handler import add_log_handler

        return add_log_handler
    if name == "release_gpu_memory":
        from .release_gpu_memory import release_gpu_memory

        return release_gpu_memory
    if name == "zip_directory":
        from .make_zip import zip_directory

        return zip_directory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
