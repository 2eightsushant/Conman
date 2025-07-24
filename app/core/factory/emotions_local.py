from optimum.onnxruntime import ORTModelForSequenceClassification
from app.shared.logger import get_logger

logger = get_logger(__name__)

class EmotionFactory:
    _model_instance = None

    @classmethod
    def get_model(cls):
        if cls._model_instance is None:
            logger.info("Initializing emotion classification model")
            cls._model_instance = ORTModelForSequenceClassification.from_pretrained(
            "SamLowe/roberta-base-go_emotions-onnx",
            subfolder="onnx",
            file_name="model_quantized.onnx"
        )
        return cls._model_instance

    @classmethod
    def clear_model(cls):
        if cls._model_instance is not None:
            logger.info("Clearing emotion classification model")
            cls._model_instance = None