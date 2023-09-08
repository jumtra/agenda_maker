import gc
from logging import getLogger

import torch

logger = getLogger()

__all__ = ["release_gpu_memory"]


def release_gpu_memory(gpu_task) -> None:
    """不要なGPUメモリーを解放"""
    logger.info("GPUメモリーを解放しました")
    del gpu_task
    gc.collect()
    torch.cuda.empty_cache()
