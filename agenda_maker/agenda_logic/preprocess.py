import logging
from pathlib import Path

import ffmpeg
from pydub import AudioSegment
from pydub.silence import split_on_silence

from agenda_maker.common import ConfigManager

logger = logging.getLogger()


def preprocess(path_input: str, config_manager: ConfigManager) -> str:
    """mp3,mp4を前処理したwav形式に変換"""

    # 拡張子の取得
    name_extention = path_input.split(".")[-1]
    path_out = path_input.split(".")[0] + f"from{name_extention}_convert_to.wav"

    if name_extention == "mp3":
        logger.info("convert to wav ... ")
        path_wav_input = mp32wav(path_input, path_out)
    elif name_extention == "mp4":
        logger.info("convert to wav ... ")
        path_wav_input = mp42wav(path_input, path_out)
    elif name_extention == "wav":
        logger.info("skip convert to wav")
        path_wav_input = path_input
    else:
        logger.error(Exception("only use mp3,mp4,wav"))
    if config_manager.config.tasks.is_wav_preprocess:
        preprocess_wav(path_input=path_wav_input, config_manager=config_manager)
    else:
        logger.info("skip preprocess wav")
    return path_wav_input


def mp32wav(path_mp3: str, path_out: str) -> str:
    sound = AudioSegment.from_mp3(Path(path_mp3))
    sound.export(Path(path_out), format="wav", parameters=["-ar", "16000"])
    logger.info("変換終了")
    return path_out


def mp42wav(path_mp4: str, path_out: str) -> str:
    stream = ffmpeg.input(Path(path_mp4))
    stream = ffmpeg.output(stream, path_out)
    ffmpeg.run(stream, quiet=True, overwrite_output=True)
    logger.info("変換終了")
    return path_out


def preprocess_wav(path_input: str, config_manager: ConfigManager) -> None:
    logger.info("前処理開始")
    sound = AudioSegment.from_file(path_input, "wav")
    sound = sound[
        config_manager.config.preprocess.cut_time.start_time : (
            sound.duration_seconds - config_manager.config.preprocess.cut_time.end_time
        )
        * 1000
    ]
    cut_silence(sound, path_output=path_input, config_manager=config_manager)
    logger.info("前処理終了")


def cut_silence(sound, path_output: str, config_manager: ConfigManager) -> None:
    min_silence_len = config_manager.config.preprocess.silence_cut.min_silence_len
    silence_thresh = config_manager.config.preprocess.silence_cut.silence_thresh
    keep_silence = config_manager.config.preprocess.silence_cut.keep_silence
    chunks = split_on_silence(
        sound,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
    )

    cutted_sound = sum(chunks)
    cutted_sound.export(path_output, format="wav", parameters=["-ar", "16000"])
