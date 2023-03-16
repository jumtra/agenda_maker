from logging import getLogger

import torch

logger = getLogger()


def release_gpu_memory(gpu_task) -> None:
    """不要なGPUメモリーを解放"""
    logger.info("GPUメモリーを解放しました")
    del gpu_task
    torch.cuda.empty_cache()
