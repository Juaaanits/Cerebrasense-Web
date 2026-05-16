from io import BytesIO

import torch
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from PIL import Image

from app.model import load_artifacts
from app.preprocess import preprocess_image
from app.schemas import PredictionResponse


MODEL_VERSION = "cnn-label-smoothing-v1"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}

app = FastAPI(title="CerebraSense Model Service")
model, scaler, metadata, device = load_artifacts()


def verify_model_token(authorization: str | None) -> None:
    # Set MODEL_API_TOKEN in production and compare it here if the service is public.
    if authorization is None:
        return


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}


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

    tensor = preprocess_image(
        image=image,
        scaler=scaler,
        img_size=metadata["img_size"],
    ).to(device)

    with torch.inference_mode():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1).squeeze().cpu().tolist()

    best_index = int(max(range(len(probabilities)), key=probabilities.__getitem__))
    class_mapping = metadata["class_mapping"]

    return {
        "predicted_label": class_mapping[best_index],
        "confidence": round(probabilities[best_index] * 100, 2),
        "probabilities": {
            class_mapping[index]: round(probability * 100, 2)
            for index, probability in enumerate(probabilities)
        },
        "model_version": MODEL_VERSION,
    }
