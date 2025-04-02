from transformers import pipeline
from typing import List, Dict, Any
import torch

from config.settings import CLASSIFICATION_MODEL, CATEGORIES
from config.logging_config import logger

class TopicClassifier:
    def __init__(self):
        try:
            # Initialize the zero-shot classification pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model=CLASSIFICATION_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            logger.error(f"Error initializing classifier: {str(e)}")
            raise
    
    def classify(self, text: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Classify the text into topics."""
        try:
            if not text:
                return []
            
            # Perform classification
            results = self.classifier(
                text,
                candidate_labels=CATEGORIES,
                multi_label=True,
                top_k=top_k
            )
            
            # Format results
            classifications = []
            for label, score in zip(results['labels'], results['scores']):
                classifications.append({
                    'category': label,
                    'confidence': float(score)
                })
            
            return classifications
        except Exception as e:
            logger.error(f"Error classifying text: {str(e)}")
            return []
    
    def get_primary_category(self, text: str) -> str:
        """Get the primary category for the text."""
        try:
            classifications = self.classify(text, top_k=1)
            if classifications:
                return classifications[0]['category']
            return 'general'
        except Exception as e:
            logger.error(f"Error getting primary category: {str(e)}")
            return 'general'
    
    def get_categories_with_confidence(self, text: str, confidence_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Get all categories with confidence above the threshold."""
        try:
            classifications = self.classify(text, top_k=len(CATEGORIES))
            return [
                cat for cat in classifications
                if cat['confidence'] >= confidence_threshold
            ]
        except Exception as e:
            logger.error(f"Error getting categories with confidence: {str(e)}")
            return []
    
    def validate_category(self, category: str) -> bool:
        """Validate if a category is in the predefined list."""
        return category in CATEGORIES 