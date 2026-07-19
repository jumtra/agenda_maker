import re

__all__ = ["remove_text_noise"]


def remove_text_noise(
    text: str,
    *,
    strip_summary_prefix: bool = False,
    strip_angle_brackets: bool = False,
    strip_hyphen: bool = False,
    strip_newlines: bool = False,
    extra_replacements: tuple[str, ...] = (),
) -> str:
    """文字起こし・要約結果からノイズ文字を除去する。"""
    if strip_summary_prefix and "要約:" in text:
        text = text.split("要約:")[-1]

    text = re.sub(r"【.*】", "", text)
    text = re.sub(r"（.*）", "", text)
    text = re.sub(r"「.*」", "", text)
    if strip_angle_brackets:
        text = re.sub(r"<.*>", "", text)
        text = re.sub(r"＜.*＞", "", text)
    text = re.sub(r"[［］\[\]]", " ", text)
    text = re.sub(r"[@＠]\w+", "", text)
    text = re.sub(r"https?:\/\/.*?[\r\n ]", "", text)
    text = re.sub(r"　", " ", text)
    text = text.replace("\u200b", "")
    text = text.replace("/", "")

    if strip_hyphen:
        text = text.replace("-", "")
    if strip_newlines:
        text = text.replace("\n", "")

    for word in extra_replacements:
        text = text.replace(word, "")

    return text
