from transformers import pipeline
from typing import Optional
import nltk
from nltk.tokenize import sent_tokenize
import torch

from config.settings import SUMMARIZATION_MODEL, MAX_SUMMARY_LENGTH
from config.logging_config import logger

class Summarizer:
    def __init__(self):
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            
            # Initialize the summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model=SUMMARIZATION_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            logger.error(f"Error initializing summarizer: {str(e)}")
            raise
    
    def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """Generate a summary of the input text."""
        try:
            if not text or len(text.split()) < 50:
                return text
            
            # Use default max_length if not specified
            if max_length is None:
                max_length = MAX_SUMMARY_LENGTH
            
            # Generate summary
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=30,
                do_sample=False
            )[0]['summary_text']
            
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return text
    
    def extractive_summarize(self, text: str, num_sentences: int = 3) -> str:
        """Generate an extractive summary using sentence scoring."""
        try:
            # Tokenize into sentences
            sentences = sent_tokenize(text)
            
            if len(sentences) <= num_sentences:
                return text
            
            # Score sentences based on position and length
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                # Position score (earlier sentences get higher scores)
                position_score = 1.0 / (i + 1)
                
                # Length score (prefer medium-length sentences)
                words = sentence.split()
                length_score = 1.0 - abs(len(words) - 15) / 30  # Optimal length around 15 words
                
                # Combined score
                score = (position_score + length_score) / 2
                scored_sentences.append((score, sentence))
            
            # Sort by score and get top sentences
            scored_sentences.sort(reverse=True)
            selected_sentences = [s[1] for s in scored_sentences[:num_sentences]]
            
            # Reorder sentences to maintain original order
            selected_sentences.sort(key=lambda x: sentences.index(x))
            
            return ' '.join(selected_sentences)
        except Exception as e:
            logger.error(f"Error generating extractive summary: {str(e)}")
            return text
    
    def hybrid_summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """Generate a hybrid summary using both abstractive and extractive methods."""
        try:
            # Generate abstractive summary
            abstractive_summary = self.summarize(text, max_length)
            
            # Generate extractive summary
            extractive_summary = self.extractive_summarize(text)
            
            # Combine both summaries
            combined_summary = f"{abstractive_summary}\n\nKey points:\n{extractive_summary}"
            
            return combined_summary
        except Exception as e:
            logger.error(f"Error generating hybrid summary: {str(e)}")
            return text 