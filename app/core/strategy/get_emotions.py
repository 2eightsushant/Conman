from transformers import AutoTokenizer, pipeline
from optimum.onnxruntime import ORTModelForSequenceClassification
from app.core.factory.emotions_local import EmotionFactory
from typing import List
from functools import lru_cache
from app.shared.logger import get_logger

logger = get_logger(__name__)

class RoBertEmotionGo:
    def __init__(self, k: int = 2):
        assert k >= 1, "k must be >= 1"
        self.k = k

        # Load tokenizer and ONNX model only once (during instantiation)
        self.tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions-onnx")
        self.model = EmotionFactory.get_model()

        # Create ONNX pipeline once and reuse
        self.onnx_classifier = pipeline(
            task="text-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            top_k=None,
            function_to_apply="sigmoid"
        )

        logger.info("Loading SamLowe/roberta-base-go_emotions-onnx model and tokenizer successfull!")

    @lru_cache(maxsize=1024)
    def get_emotions(self, text: str) -> List[str]:
        """
        Predicts the top-k emotions from a given string using ONNX-optimized RoBERTa.
        Caches results for repeated text inputs.
        """
        result = self.onnx_classifier(text)
        top_k = sorted(result[0], key=lambda x: x["score"], reverse=True)[:self.k]
        return [label["label"] for label in top_k]