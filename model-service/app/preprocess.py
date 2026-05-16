import torch
from PIL import Image, ImageOps
from torchvision import transforms


def preprocess_image(image: Image.Image, bundle: dict) -> torch.Tensor:
    transform = transforms.Compose(
        [
            transforms.Resize((bundle["image_size"], bundle["image_size"])),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=bundle["imagenet_mean"],
                std=bundle["imagenet_std"],
            ),
        ]
    )

    image = ImageOps.exif_transpose(image).convert("RGB")
    return transform(image).unsqueeze(0).to(dtype=torch.float32)
