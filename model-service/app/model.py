import pickle
from pathlib import Path

import torch
import torch.nn as nn


BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"


class CNN(nn.Module):
    def __init__(self, img_size: int):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        with torch.no_grad():
            dummy = torch.zeros(1, 1, img_size, img_size)
            n = self.conv(dummy).view(1, -1).shape[1]

        self.fc = nn.Sequential(
            nn.Linear(n, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 4),
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def load_artifacts():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(MODELS_DIR / "metadata.pkl1", "rb") as metadata_file:
        metadata = pickle.load(metadata_file)

    with open(MODELS_DIR / "scaler.pkl1", "rb") as scaler_file:
        scaler = pickle.load(scaler_file)

    model = CNN(metadata["img_size"])
    model.load_state_dict(
        torch.load(MODELS_DIR / "cnn_model1.pt", map_location=device)
    )
    model.to(device)
    model.eval()

    return model, scaler, metadata, device
