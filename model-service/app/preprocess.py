import numpy as np
import torch
from PIL import Image


def preprocess_image(image: Image.Image, scaler, img_size: int) -> torch.Tensor:
    image = image.convert("L")
    image = image.resize((img_size, img_size))

    pixels = np.array(image).astype(np.float32)
    flattened = pixels.reshape(1, -1)
    scaled = scaler.transform(flattened)

    return torch.tensor(
        scaled.reshape(1, 1, img_size, img_size),
        dtype=torch.float32,
    )
