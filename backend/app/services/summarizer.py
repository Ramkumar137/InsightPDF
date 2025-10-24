"""
AI-powered text summarization service using Hugging Face Transformers
"""
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from typing import Dict
from app.config import settings

class SummarizationService:
    """Service for generating AI summaries with context awareness"""
    
    def __init__(self):
        """Initialize T5 model and tokenizer (CPU-friendly)"""
        print(f"Loading model: {settings.MODEL_NAME}")
        self.tokenizer = T5Tokenizer.from_pretrained(settings.MODEL_NAME)
        self.model = T5ForConditionalGeneration.from_pretrained(settings.MODEL_NAME)
        
        # Force CPU usage (no CUDA)
        self.device = "cpu"
        self.model = self.model.to(self.device)
        print(f"✅ Model loaded on {self.device}")
    
    def generate_summary(
        self,
        text: str,
        context_type: str,
        max_length: int = None,
        min_length: int = None
    ) -> str:
        """
        Generate summary for given text with context awareness.
        
        Args:
            text: Input text to summarize
            context_type: One of executive/student/analyst/general
            max_length: Maximum summary length (tokens)
            min_length: Minimum summary length (tokens)
            
        Returns:
            Generated summary text
        """
        # Get context-specific prompt
        context_prompt = settings.CONTEXT_PROMPTS.get(
            context_type,
            settings.CONTEXT_PROMPTS["general"]
        )
        
        # Truncate input text if needed
        truncated_text = text[:settings.MAX_INPUT_LENGTH]
        
        # Create prompt
        prompt = f"{context_prompt}\n\nDocument: {truncated_text}"
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Generate summary
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length or settings.MAX_SUMMARY_LENGTH,
                min_length=min_length or settings.MIN_SUMMARY_LENGTH,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3
            )
        
        # Decode output
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary
    
    def generate_structured_summary(
        self,
        text: str,
        context_type: str
    ) -> Dict[str, str]:
        """
        Generate structured summary with multiple sections.
        
        Args:
            text: Input text
            context_type: Summary context type
            
        Returns:
            Dictionary with overview, keyInsights, risks, recommendations
        """
        # Generate main overview
        overview = self.generate_summary(
            text,
            context_type,
            max_length=200,
            min_length=80
        )
        
        # Generate key insights
        insights_prompt = "Extract and list the key insights and important points from this document:"
        key_insights = self.generate_summary(
            f"{insights_prompt}\n\n{text}",
            context_type,
            max_length=150,
            min_length=50
        )
        
        # Context-specific sections
        risks = ""
        recommendations = ""
        
        if context_type in ["executive", "analyst"]:
            # Generate risks section
            risks_prompt = "Identify potential risks, challenges, or concerns mentioned in this document:"
            risks = self.generate_summary(
                f"{risks_prompt}\n\n{text}",
                context_type,
                max_length=120,
                min_length=40
            )
            
            # Generate recommendations
            rec_prompt = "Provide actionable recommendations based on this document:"
            recommendations = self.generate_summary(
                f"{rec_prompt}\n\n{text}",
                context_type,
                max_length=150,
                min_length=50
            )
        
        return {
            "overview": overview,
            "keyInsights": key_insights,
            "risks": risks,
            "recommendations": recommendations
        }
    
    def shorten_summary(self, text: str, context_type: str) -> str:
        """
        Generate a shorter version of existing summary.
        
        Args:
            text: Original summary text
            context_type: Context type
            
        Returns:
            Shortened summary
        """
        return self.generate_summary(
            text,
            context_type,
            max_length=100,
            min_length=40
        )
    
    def refine_summary(self, text: str, context_type: str) -> str:
        """
        Refine and improve existing summary for clarity.
        
        Args:
            text: Original summary text
            context_type: Context type
            
        Returns:
            Refined summary
        """
        refine_prompt = "Improve the clarity and remove redundancy from this summary:"
        return self.generate_summary(
            f"{refine_prompt}\n\n{text}",
            context_type,
            max_length=250,
            min_length=80
        )

# Global summarization service instance
summarization_service = SummarizationService()