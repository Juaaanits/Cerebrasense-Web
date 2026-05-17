import os
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import torch
import torch.nn as nn
from torchvision import models


BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"
BUNDLE_PATH = MODELS_DIR / "cerebrasense_improved_bundle.pt"
LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec"


def _is_lfs_pointer(path: Path) -> bool:
    if not path.exists():
        return False

    with path.open("rb") as model_file:
        return model_file.read(len(LFS_POINTER_PREFIX)) == LFS_POINTER_PREFIX


def _ensure_bundle_file() -> None:
    bundle_url = os.getenv("MODEL_BUNDLE_URL")
    has_usable_bundle = BUNDLE_PATH.exists() and not _is_lfs_pointer(BUNDLE_PATH)

    if has_usable_bundle:
        return

    if not bundle_url:
        if BUNDLE_PATH.exists() and _is_lfs_pointer(BUNDLE_PATH):
            raise RuntimeError(
                "Model bundle is a Git LFS pointer, not the real .pt file. "
                "Set MODEL_BUNDLE_URL in Railway so the service can download "
                "cerebrasense_improved_bundle.pt during startup."
            )

        raise FileNotFoundError(
            f"Missing model bundle at {BUNDLE_PATH}. Set MODEL_BUNDLE_URL "
            "in Railway or provide the bundle at model-service/models/."
        )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model bundle to {BUNDLE_PATH}...")
    urlretrieve(bundle_url, BUNDLE_PATH)

    if _is_lfs_pointer(BUNDLE_PATH):
        raise RuntimeError(
            "Downloaded MODEL_BUNDLE_URL still points to a Git LFS pointer. "
            "Use a direct download URL for the real .pt binary."
        )


def _torch_load(path: Path, device: torch.device) -> dict[str, Any]:
    try:
        return torch.load(path, map_location=device, weights_only=False)
    except TypeError:
        return torch.load(path, map_location=device)


def build_model(model_name: str, num_classes: int) -> nn.Module:
    model_name = model_name.lower()

    if model_name == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.30),
            nn.Linear(in_features, num_classes),
        )
        return model

    if model_name == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model

    if model_name == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=None)
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, num_classes)
        return model

    raise ValueError(f"Unsupported model_name in bundle: {model_name}")


def load_artifacts():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _ensure_bundle_file()
    bundle = _torch_load(BUNDLE_PATH, device)

    class_names = bundle["class_names"]
    model = build_model(bundle["model_name"], num_classes=len(class_names))
    model.load_state_dict(bundle["model_state"])
    model.to(device)
    model.eval()

    return model, bundle, device
