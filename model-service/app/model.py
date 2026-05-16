from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torchvision import models


BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"
BUNDLE_PATH = MODELS_DIR / "cerebrasense_improved_bundle.pt"


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
    bundle = _torch_load(BUNDLE_PATH, device)

    class_names = bundle["class_names"]
    model = build_model(bundle["model_name"], num_classes=len(class_names))
    model.load_state_dict(bundle["model_state"])
    model.to(device)
    model.eval()

    return model, bundle, device
