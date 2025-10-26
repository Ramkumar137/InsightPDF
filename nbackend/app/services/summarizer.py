"""
AI-powered summarization using Google Gemini API
UPGRADED: Fast, high-quality summaries with context awareness
"""
import google.generativeai as genai
from typing import Dict, List
import os
from app.config import settings
from dotenv import load_dotenv

load_dotenv()
class SummarizationService:
    """Service for generating AI summaries using Gemini"""
    
    def __init__(self):
        """Initialize Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Gemini API initialized successfully")
    
    def generate_summary(
        self,
        text: str,
        context_type: str,
        max_length: int = None
    ) -> str:
        """
        Generate summary using Gemini API.
        
        Args:
            text: Input text to summarize
            context_type: executive/student/analyst/general
            max_length: Optional target length
            
        Returns:
            Generated summary text
        """
        # Get context-specific prompt
        context_prompt = settings.CONTEXT_PROMPTS.get(
            context_type,
            settings.CONTEXT_PROMPTS["general"]
        )
        
        # Build prompt
        length_instruction = ""
        if max_length:
            if max_length < 150:
                length_instruction = "Keep the summary very concise (2-3 sentences)."
            elif max_length < 250:
                length_instruction = "Provide a brief summary (4-5 sentences)."
            else:
                length_instruction = "Provide a comprehensive summary."
        
        prompt = f"""
{context_prompt}

{length_instruction}

Document to summarize:
{text[:50000]}  # Limit to first 50k chars for API

Provide a clear, well-structured summary.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            # Fallback to basic summary
            return self._basic_summary(text, max_length or 250)
    
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
        context_prompt = settings.CONTEXT_PROMPTS.get(
            context_type,
            settings.CONTEXT_PROMPTS["general"]
        )
        
        # Context-specific sections
        sections_to_include = {
            "executive": ["overview", "insights", "risks", "recommendations"],
            "analyst": ["overview", "insights", "risks", "recommendations"],
            "student": ["overview", "insights"],
            "general": ["overview", "insights"]
        }
        
        sections = sections_to_include.get(context_type, ["overview", "insights"])
        
        # Build comprehensive prompt
        prompt = f"""
You are an expert summarizer. {context_prompt}

Analyze the following document and provide a structured summary with these sections:

"""
        
        if "overview" in sections:
            prompt += "1. OVERVIEW: A comprehensive summary of the main content (3-4 paragraphs)\n"
        
        if "insights" in sections:
            prompt += "2. KEY INSIGHTS: The most important findings, concepts, or takeaways (3-5 bullet points)\n"
        
        if "risks" in sections:
            prompt += "3. RISKS & CHALLENGES: Potential issues, concerns, or challenges mentioned (3-4 bullet points)\n"
        
        if "recommendations" in sections:
            prompt += "4. RECOMMENDATIONS: Actionable suggestions or next steps (3-4 bullet points)\n"
        
        prompt += f"""
Document:
{text[:50000]}

Format your response EXACTLY as:
[OVERVIEW]
Your overview here...

[KEY INSIGHTS]
Your insights here...

[RISKS]
Your risks here...

[RECOMMENDATIONS]
Your recommendations here...
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Parse structured response
            sections_dict = self._parse_sections(result_text)
            
            return {
                "overview": sections_dict.get("overview", "Summary not available"),
                "keyInsights": sections_dict.get("key insights", "No insights available"),
                "risks": sections_dict.get("risks", "") if "risks" in sections else "",
                "recommendations": sections_dict.get("recommendations", "") if "recommendations" in sections else ""
            }
            
        except Exception as e:
            print(f"❌ Structured summary error: {e}")
            # Fallback to basic summary
            basic = self._basic_summary(text, 500)
            return {
                "overview": basic,
                "keyInsights": "Please try regenerating for detailed insights.",
                "risks": "",
                "recommendations": ""
            }
    
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Parse structured response into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split("\n")
        
        for line in lines:
            line_upper = line.strip().upper()
            
            # Check for section headers
            if "[OVERVIEW]" in line_upper or line_upper == "OVERVIEW":
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "overview"
                current_content = []
            elif "[KEY INSIGHTS]" in line_upper or "KEY INSIGHTS" in line_upper:
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "key insights"
                current_content = []
            elif "[RISKS" in line_upper or line_upper.startswith("RISKS"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "risks"
                current_content = []
            elif "[RECOMMENDATIONS]" in line_upper or "RECOMMENDATIONS" in line_upper:
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "recommendations"
                current_content = []
            elif current_section and line.strip():
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()
        
        return sections
    
    def shorten_summary(self, text: str, context_type: str) -> str:
        """Generate shorter version of summary"""
        prompt = f"""
Shorten this summary to 2-3 concise sentences while keeping the most important information:

{text}

Provide only the shortened version.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            # Fallback: just take first few sentences
            sentences = text.split(". ")
            return ". ".join(sentences[:3]) + "."
    
    def refine_summary(self, text: str, context_type: str) -> str:
        """Improve clarity and remove redundancy"""
        prompt = f"""
Improve this summary by:
- Enhancing clarity
- Removing redundancy
- Making it more professional
- Keeping the same length

Original summary:
{text}

Provide the refined version.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return text  # Return original if API fails
    
    def _basic_summary(self, text: str, max_length: int) -> str:
        """Fallback: Basic extractive summary"""
        sentences = text.split(". ")
        summary_sentences = sentences[:min(5, len(sentences))]
        return ". ".join(summary_sentences) + "."

# Global service instance
summarization_service = SummarizationService()