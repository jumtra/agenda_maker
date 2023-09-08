import numpy as np
from janome.tokenizer import Tokenizer

__all__ = ["texttiling_japanese"]


def texttiling_japanese(text: str, w: int, k: int) -> list[str]:
    return _texttiling_core(text, w, k)


def _texttiling_core(text: str, w: int, k: int) -> list[str]:
    """
    text: 日本語の文章
    w: 窓の幅
    k: ブロックの数
    """
    # Janomeでトークン化
    t = Tokenizer()
    tokens = list(t.tokenize(text, wakati=True))

    # ブロックを作成
    blocks = [tokens[i : i + w] for i in range(0, len(tokens), w)]

    # スコアを計算
    scores = []
    for i in range(len(blocks) - 1):
        block1 = blocks[i]
        block2 = blocks[i + 1]
        score = 0
        for word in set(block1 + block2):
            count1 = block1.count(word)
            count2 = block2.count(word)
            score += abs(count1 - count2)
        scores.append(score)

    # 平均と標準偏差を計算
    mean = np.mean(scores)
    std_dev = np.std(scores)

    # 境界値を計算
    cutoffs = [mean - std_dev] * k

    # 境界値を探索
    boundaries = []
    depth_scores = []
    for i in range(len(scores) - k + 1):
        depth_score = sum([cutoffs[j] - scores[i + j] for j in range(k)])
        depth_scores.append(depth_score)
        if depth_score > 0:
            boundaries.append(i + int(k / 2))

    # 境界値に基づいて文章を分割
    segments = []
    start_index = 0
    for boundary in boundaries:
        end_index = boundary * w
        segment = "".join(tokens[start_index:end_index])
        segments.append(segment)
        start_index = end_index
    segment = "".join(tokens[start_index:])
    segments.append(segment)

    return segments
