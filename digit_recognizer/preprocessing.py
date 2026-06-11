from __future__ import annotations

from typing import Iterable

import torch

MNIST_MEAN = 0.1307
MNIST_STD = 0.3081


def pixels_to_tensor(pixels: Iterable[object]) -> torch.Tensor:
    values = []
    for value in pixels:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("pixels 中只能包含数字。") from exc
        if not 0 <= number <= 255:
            raise ValueError("pixels 的取值范围必须是 0 到 255。")
        values.append(number / 255.0)

    if len(values) != 28 * 28:
        raise ValueError("pixels 必须包含 784 个数值。")

    tensor = torch.tensor(values, dtype=torch.float32).view(1, 1, 28, 28)
    return (tensor - MNIST_MEAN) / MNIST_STD
