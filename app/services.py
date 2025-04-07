# app/services.py
import logging
import string
from typing import Dict, Any
from functools import lru_cache

import torch
import torch.nn.functional as F
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    PreTrainedTokenizer,
    PreTrainedModel
)

from app.config import settings
from app.exceptions import ModelLoadError, ModelInferenceError

logger = logging.getLogger(__name__)

class TextDetectionService:
    """
    Manages the AI text detection model loading and inference.
    Implemented as a Singleton to prevent reloading the model.
    """
    _instance = None
    _tokenizer: PreTrainedTokenizer | None = None
    _model: PreTrainedModel | None = None
    _device: torch.device | None = None
    _initialized: bool = False # Class-level flag to ensure single initialization

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TextDetectionService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if TextDetectionService._initialized:
            return # Prevent re-initialization

        logger.info("Initializing TextDetectionService...")
        self._determine_device()
        self._load_model_and_tokenizer()
        TextDetectionService._initialized = True
        logger.info(f"TextDetectionService initialized on device: {self._device}")

    def _determine_device(self):
        """Sets the computation device (CUDA or CPU)."""
        if torch.cuda.is_available():
            self._device = torch.device("cuda")
            logger.info("Using CUDA device for inference.")
        else:
            self._device = torch.device("cpu")
            logger.info("Using CPU device for inference.")
        settings.DEVICE = str(self._device)

    def _load_model_and_tokenizer(self):
        """Loads the tokenizer and model from Hugging Face Hub."""
        try:
            logger.info(f"Loading tokenizer: {settings.MODEL_NAME}")
            self._tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME, token=settings.HF_TOKEN)
            logger.info(f"Loading model: {settings.MODEL_NAME}")
            self._model = AutoModelForSequenceClassification.from_pretrained(settings.MODEL_NAME, token=settings.HF_TOKEN)

            if self._model and self._device:
                self._model.to(self._device)
                self._model.eval() # Set model to evaluation mode for inference
                logger.info(f"Model '{settings.MODEL_NAME}' loaded to {self._device}.")
            else:
                raise ModelLoadError("Model or device invalid after loading attempt.")
        except Exception as e:
            logger.error(f"Failed to load model or tokenizer '{settings.MODEL_NAME}': {e}", exc_info=True)
            # Catching general Exception, specific ones (ImportError, OSError) handled by base class
            raise ModelLoadError(f"Failed loading resources: {e}") from e


    def predict(self, text: str) -> Dict[str, Any]:
        """Runs inference on the input text."""
        if not TextDetectionService._initialized or not self._model or not self._tokenizer or not self._device:
             logger.error("Prediction attempt on uninitialized service.")
             raise ModelInferenceError("Prediction service is not ready.")

        processed_text = text.translate(str.maketrans('', '', string.punctuation)).strip()
        # Note: Prediction continues even if processed_text is empty, tokenizer/model might handle it.

        try:
            inputs = self._tokenizer(
                processed_text,
                padding="max_length",
                truncation=True,
                max_length=settings.MODEL_MAX_LENGTH,
                return_tensors="pt"
            ).to(self._device) # Move inputs to the correct device directly

            # Disable gradient calculations for efficiency
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=1).squeeze()

            probabilities_cpu = probabilities.cpu().numpy()
            predicted_class_id = probabilities_cpu.argmax().item()

            result = {
                "softmax_score_class_0": float(probabilities_cpu[0]),
                "softmax_score_class_1": float(probabilities_cpu[1]),
                "predicted_class": int(predicted_class_id),
                "predicted_label": "AI-generated" if predicted_class_id == 1 else "Human-written"
            }
            return result

        except Exception as e:
            logger.error(f"Model inference failed: {e}", exc_info=True)
            raise ModelInferenceError(f"Inference error: {e}")


@lru_cache()
def get_text_detection_service() -> TextDetectionService:
    """Dependency injector providing the singleton TextDetectionService instance."""
    try:
        # Instantiation handles the initialization logic via __init__
        return TextDetectionService()
    except ModelLoadError as e:
         logger.critical(f"Failed to get/initialize TextDetectionService: {e}", exc_info=True)
         # Propagate runtime error if service cannot be instantiated (e.g., model load failed)
         raise RuntimeError(f"Service initialization failed: {e}") from e