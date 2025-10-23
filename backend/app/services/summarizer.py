from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from typing import List
from app.config import settings


class SummarizerService:
    """
    AI-powered summarization service using T5 model
    """

    # Context-specific prompts
    CONTEXT_PROMPTS = {
        "executive": "Summarize this document with a focus on high-level insights, strategic decisions, and key business outcomes:",
        "student": "Summarize this document with clear explanations, learning insights, and important concepts:",
        "analyst": "Summarize this document highlighting trends, data points, statistical analysis, and key findings:",
        "general": "Summarize this document briefly and clearly:"
    }

    def __init__(self):
        print("Loading T5 model...")
        self.tokenizer = T5Tokenizer.from_pretrained(settings.MODEL_NAME)
        self.model = T5ForConditionalGeneration.from_pretrained(settings.MODEL_NAME)

        # Set to CPU mode
        self.device = torch.device("cpu")
        self.model.to(self.device)
        self.model.eval()

        print("T5 model loaded successfully!")

    def generate_summary(
            self,
            text: str,
            context_type: str = "general",
            max_length: int = None,
            min_length: int = None
    ) -> str:
        """
        Generate summary based on context type

        Args:
            text: Input text to summarize
            context_type: Type of context (executive, student, analyst, general)
            max_length: Maximum length of summary
            min_length: Minimum length of summary

        Returns:
            Generated summary
        """
        # Get context prompt
        prompt = self.CONTEXT_PROMPTS.get(context_type.lower(), self.CONTEXT_PROMPTS["general"])

        # Truncate text if too long
        truncated_text = text[:settings.MAX_INPUT_LENGTH]

        # Prepare input
        input_text = f"{prompt} {truncated_text}"

        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        # Set lengths
        max_len = max_length or settings.MAX_SUMMARY_LENGTH
        min_len = min_length or settings.MIN_SUMMARY_LENGTH

        # Generate summary
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_len,
                min_length=min_len,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )

        # Decode
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return summary

    def summarize_chunks(
            self,
            chunks: List[str],
            context_type: str = "general"
    ) -> str:
        """
        Summarize multiple text chunks and combine them

        Args:
            chunks: List of text chunks
            context_type: Type of context

        Returns:
            Combined summary
        """
        summaries = []

        for chunk in chunks:
            summary = self.generate_summary(chunk, context_type)
            summaries.append(summary)

        # If multiple summaries, combine and summarize again
        if len(summaries) > 1:
            combined = " ".join(summaries)
            final_summary = self.generate_summary(combined, context_type)
            return final_summary

        return summaries[0] if summaries else ""

    def shorten_summary(self, summary: str, context_type: str = "general") -> str:
        """
        Create a shorter version of existing summary
        """
        return self.generate_summary(
            summary,
            context_type,
            max_length=150,
            min_length=50
        )

    def refine_summary(self, summary: str, context_type: str = "general") -> str:
        """
        Refine and improve existing summary
        """
        prompt = f"Improve clarity and remove redundancy from this summary: {summary}"

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=settings.MAX_SUMMARY_LENGTH,
                min_length=settings.MIN_SUMMARY_LENGTH,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )

        refined = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return refined


# Initialize singleton instance
summarizer_instance = None


def get_summarizer() -> SummarizerService:
    """
    Get or create summarizer instance (singleton pattern)
    """
    global summarizer_instance
    if summarizer_instance is None:
        summarizer_instance = SummarizerService()
    return summarizer_instance