from transformers import AutoTokenizer, pipeline
from optimum.onnxruntime import ORTModelForSequenceClassification
from app.config.settings import settings
from app.shared.logger import get_logger

logger = get_logger(__name__)

class OnnxPipeline:
    def __init__(self):
        self.pipeline = None
        self.tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions-onnx")

    def init_pipeline(self, model):
        try:
            self.pipeline = pipeline(
            task="text-classification",
            model=model,
            tokenizer=self.tokenizer,
            top_k=None,
            function_to_apply="sigmoid"
        )
            logger.info(f"Onnx pipeline initialized")
        except Exception as e:
            logger.error(f"Onnx pipeline initialization failed: {str(e)}")
            raise

    def get(self) -> pipeline:
        if not self.pipeline:
            logger.info("Onnx pipeline not initialized")
            raise RuntimeError("Onnx pipeline not initialized")
        return self.pipeline

    def delete(self):
        logger.info("Onnx pipeline delete")
        self.pipeline = None
