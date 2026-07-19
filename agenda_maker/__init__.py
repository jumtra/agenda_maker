"""agenda_maker: 音声・動画から議事録を生成するライブラリ。"""

__all__ = ["make_agenda"]


def __getattr__(name: str):
    if name == "make_agenda":
        from agenda_maker.main import make_agenda

        return make_agenda
    if name == "app":
        from agenda_maker.app import app

        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
