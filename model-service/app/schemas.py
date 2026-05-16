from pydantic import BaseModel


class PredictionResponse(BaseModel):
    predicted_label: str
    display_label: str
    confidence: float
    probabilities: dict[str, float]
    model_version: str
    is_uncertain: bool
    confidence_threshold: float
