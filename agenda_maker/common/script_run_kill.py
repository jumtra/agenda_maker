import logging
import subprocess
import sys

logger = logging.getLogger(__name__)

__all__ = ["script_run"]


def script_run(script: str, cmd: list[str]) -> None:
    """外部スクリプトを実行し、失敗時は例外を送出する。"""
    process = None
    command = [sys.executable, script, *cmd]
    try:
        process = subprocess.Popen(command)
        returncode = process.wait()
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, command)
    except Exception as e:
        logger.error(f"エラー: {e}")
        raise
    finally:
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except Exception as e:
                logger.error(f"プロセスのキル時にエラーが発生しました: {e}")
