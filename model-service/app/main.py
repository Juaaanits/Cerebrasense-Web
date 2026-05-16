from io import BytesIO

import torch
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from PIL import Image

from app.model import load_artifacts
from app.preprocess import preprocess_image
from app.schemas import PredictionResponse


MODEL_VERSION = "efficientnet-b0-transfer-calibrated-v1"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}

app = FastAPI(title="CerebraSense Model Service")
model, bundle, device = load_artifacts()


def verify_model_token(authorization: str | None) -> None:
    # Set MODEL_API_TOKEN in production and compare it here if the service is public.
    if authorization is None:
        return


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "model_name": bundle["model_name"],
        "image_size": bundle["image_size"],
        "confidence_threshold": bundle["confidence_threshold"],
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    authorization: str | None = Header(default=None),
):
    verify_model_token(authorization)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG files are allowed.",
        )

    image_bytes = await file.read()
    image = Image.open(BytesIO(image_bytes))

    tensor = preprocess_image(image=image, bundle=bundle).to(device)

    with torch.inference_mode():
        logits = model(tensor)
        logits = logits / max(float(bundle["temperature"]), 1e-6)
        probabilities = torch.softmax(logits, dim=1).squeeze().cpu().tolist()

    best_index = int(max(range(len(probabilities)), key=probabilities.__getitem__))
    class_names = bundle["class_names"]
    display_names = bundle["display_names"]
    predicted_label = class_names[best_index]
    confidence = probabilities[best_index]
    confidence_threshold = float(bundle["confidence_threshold"])

    return {
        "predicted_label": predicted_label,
        "display_label": display_names[predicted_label],
        "confidence": round(confidence * 100, 2),
        "probabilities": {
            class_names[index]: round(probability * 100, 2)
            for index, probability in enumerate(probabilities)
        },
        "model_version": MODEL_VERSION,
        "is_uncertain": confidence < confidence_threshold,
        "confidence_threshold": round(confidence_threshold * 100, 2),
    }
