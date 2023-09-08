from logging import FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path

__all__ = ["add_log_handler"]


def add_log_handler(output_dir):
    """
    同じログファイルに出力する'verbose_logger'と'simple_logger'という2種類のロガーを作成します。
    'verbose_logger'は実行時間、ログレベル、モジュール名、関数名とメッセージを出力するロガーです。
    'simple_logger'はメッセージのみを出力するロガーです。

    Parameters
    ----------
    output_dir : ログファイルを配置するディレクトリ
    """
    verbose_fmt = Formatter("%(asctime)s %(levelname)-6s %(name)s %(lineno)d [%(funcName)s] %(message)s")

    # 同じloggerを参照してしまうため、loggerの名前にdateを追記するために必要。
    # https://docs.python.org/ja/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
    # > logging.getLogger('someLogger') の複数回の呼び出しは同じ logger への参照を返します。
    verbose_logger = getLogger()
    verbose_logger.setLevel("DEBUG")

    handler = StreamHandler()
    handler.setLevel("INFO")
    handler.setFormatter(verbose_fmt)
    verbose_logger.addHandler(handler)

    log_file = Path(f"{output_dir}/log.log")
    if log_file.exists():
        try:
            log_file.unlink()
        except OSError as e:
            print(f"Error:{ e.strerror}")
    handler = FileHandler(log_file, mode="a", encoding="utf8")
    handler.setLevel("DEBUG")
    handler.setFormatter(verbose_fmt)
    verbose_logger.addHandler(handler)

    # simple_logger = getLogger(f"simple_logger")
    # simple_fmt = Formatter("%(message)s")
    # simple_logger.setLevel("DEBUG")
    # handler = StreamHandler()
    # handler.setLevel("INFO")
    # handler.setFormatter(simple_fmt)
    # simple_logger.addHandler(handler)

    # handler = FileHandler(f"{output_dir}/simple_log.log", mode="a", encoding="utf8")
    # handler.setLevel("DEBUG")
    # handler.setFormatter(simple_fmt)
    # simple_logger.addHandler(handler)
    verbose_logger.info(f"log_file = {log_file}")
    return verbose_logger
