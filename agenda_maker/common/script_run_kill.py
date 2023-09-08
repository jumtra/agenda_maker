import logging
import subprocess

logger = logging.getLogger()


__all__ = ["script_run"]


def script_run(script: str, cmd: list[str]):
    try:
        # スクリプトを実行し、実行したプロセスオブジェクトを取得
        process = subprocess.Popen(["python", script, *cmd])

        # スクリプトが終了するまで待つ
        process.wait()

    except Exception as e:
        logger.error(f"エラー: {e}")
    finally:
        # プロセスをキル
        try:
            if process.poll() is None:
                process.terminate()
        except Exception as e:
            logger.error(f"プロセスのキル時にエラーが発生しました: {e}")
