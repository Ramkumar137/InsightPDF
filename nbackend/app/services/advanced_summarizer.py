"""
Advanced AI Summarization with Hybrid Approach and Enhanced Features
NEW: Extractive + Abstractive, Keyword Extraction, Section Parsing
"""
import google.generativeai as genai
from typing import Dict, List, Tuple
import os
import re
from collections import Counter
from app.config import settings
from dotenv import load_dotenv

load_dotenv()

class AdvancedSummarizationService:
    """Enhanced summarization with hybrid approach and advanced features"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Advanced Summarizer initialized")

    def generate_hybrid_summary(
        self,
        text: str,
        context_type: str,
        user_role: str = "general",
        is_private: bool = False
    ) -> Dict:
        """
        Generate hybrid summary combining extractive and abstractive approaches.

        Args:
            text: Input document text
            context_type: Context (executive/student/analyst/general)
            user_role: User role (student/researcher/professional)
            is_private: Privacy flag for memory system

        Returns:
            Complete summary with all enhancements
        """
        print(f"📊 Generating hybrid summary - Role: {user_role}, Context: {context_type}")

        # 1. Extract keywords first
        keywords = self._extract_keywords(text)

        # 2. Detect and parse sections
        sections = self._parse_document_sections(text)

        # 3. Generate extractive summary (key sentences)
        extractive = self._extractive_summarization(text, keywords)

        # 4. Generate abstractive summary with role adaptation
        abstractive_content = self._generate_role_adapted_summary(
            text, context_type, user_role, keywords
        )

        # 5. Determine memory type based on privacy
        memory_type = "short_term" if is_private else "long_term"

        return {
            "overview": abstractive_content["overview"],
            "keyInsights": abstractive_content["keyInsights"],
            "risks": abstractive_content.get("risks", ""),
            "recommendations": abstractive_content.get("recommendations", ""),
            "extractiveSummary": extractive,
            "abstractiveSummary": abstractive_content["overview"],
            "keywords": keywords,
            "sections": sections,
            "memoryType": memory_type,
            "isPrivate": is_private
        }

    def _extract_keywords(self, text: str, top_n: int = 15) -> List[str]:
        """
        Extract important keywords using AI and frequency analysis.
        """
        prompt = f"""
Extract the 15 most important keywords or key phrases from this document.
Return ONLY a comma-separated list, no explanations.

Document:
{text[:10000]}

Keywords:
"""

        try:
            response = self.model.generate_content(prompt)
            keywords_text = response.text.strip()
            keywords = [k.strip() for k in keywords_text.split(",")]
            return keywords[:top_n]
        except:
            # Fallback: frequency-based extraction
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            common_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'their', 'which'}
            filtered = [w for w in words if w not in common_words]
            counter = Counter(filtered)
            return [word for word, _ in counter.most_common(top_n)]

    def _parse_document_sections(self, text: str) -> Dict[str, str]:
        """
        Detect and extract common document sections.
        Looks for: Abstract, Introduction, Methodology, Results, Conclusion, References
        """
        sections = {}

        # Common section headers
        section_patterns = {
            "abstract": r"(?i)abstract[:\s]+(.*?)(?=\n\s*\n|\n[A-Z]|introduction|$)",
            "introduction": r"(?i)introduction[:\s]+(.*?)(?=\n\s*\n[A-Z]|methodology|methods|$)",
            "methodology": r"(?i)(?:methodology|methods)[:\s]+(.*?)(?=\n\s*\n[A-Z]|results|$)",
            "results": r"(?i)results[:\s]+(.*?)(?=\n\s*\n[A-Z]|discussion|conclusion|$)",
            "conclusion": r"(?i)conclusion[:\s]+(.*?)(?=\n\s*\n[A-Z]|references|$)"
        }

        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Limit section length
                sections[section_name] = content[:1000] if len(content) > 1000 else content

        return sections

    def _extractive_summarization(self, text: str, keywords: List[str]) -> str:
        """
        Extractive summarization: Select most important sentences based on keywords.
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        # Score sentences based on keyword presence
        scored_sentences = []
        for sentence in sentences[:100]:  # Limit to first 100 sentences
            score = sum(1 for keyword in keywords if keyword.lower() in sentence.lower())
            if score > 0:
                scored_sentences.append((score, sentence))

        # Sort by score and take top sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        top_sentences = [sent for _, sent in scored_sentences[:5]]

        return " ".join(top_sentences) + "."

    def _generate_role_adapted_summary(
        self,
        text: str,
        context_type: str,
        user_role: str,
        keywords: List[str]
    ) -> Dict[str, str]:
        """
        Generate abstractive summary adapted to user role.
        """
        # Role-specific instructions
        role_prompts = {
            "student": """
You are summarizing for a STUDENT. Focus on:
- Clear explanations of concepts and terminology
- Learning objectives and educational value
- Simplified language without losing accuracy
- Examples and applications for better understanding
- Study-friendly structure
""",
            "researcher": """
You are summarizing for a RESEARCHER. Focus on:
- Methodological details and research design
- Novel findings and contributions to the field
- Statistical significance and data analysis
- Theoretical frameworks and implications
- References to related work and future research directions
""",
            "professional": """
You are summarizing for a PROFESSIONAL. Focus on:
- Practical applications and business value
- Implementation considerations and feasibility
- ROI and cost-benefit analysis
- Strategic implications and competitive advantage
- Actionable recommendations and next steps
"""
        }

        role_instruction = role_prompts.get(user_role, role_prompts["professional"])
        context_prompt = settings.CONTEXT_PROMPTS.get(context_type, settings.CONTEXT_PROMPTS["general"])

        # Include keywords in prompt for focus
        keywords_str = ", ".join(keywords[:10])

        prompt = f"""
{role_instruction}

{context_prompt}

Key terms to focus on: {keywords_str}

Analyze this document and provide a structured summary:

1. OVERVIEW: Comprehensive summary (3-4 paragraphs)
2. KEY INSIGHTS: Most important findings (4-6 bullet points)
3. RISKS & CHALLENGES: Potential issues (if applicable)
4. RECOMMENDATIONS: Actionable next steps (if applicable)

Document:
{text[:50000]}

Format as:
[OVERVIEW]
...

[KEY INSIGHTS]
...

[RISKS]
...

[RECOMMENDATIONS]
...
"""

        try:
            response = self.model.generate_content(prompt)
            sections = self._parse_ai_sections(response.text)

            return {
                "overview": sections.get("overview", "Summary not available"),
                "keyInsights": sections.get("key insights", "No insights available"),
                "risks": sections.get("risks", ""),
                "recommendations": sections.get("recommendations", "")
            }
        except Exception as e:
            print(f"❌ AI summary error: {e}")
            return {
                "overview": "Summary generation failed. Please try again.",
                "keyInsights": "Unable to generate insights.",
                "risks": "",
                "recommendations": ""
            }

    def _parse_ai_sections(self, text: str) -> Dict[str, str]:
        """Parse AI-generated structured response."""
        sections = {}
        current_section = None
        current_content = []

        for line in text.split("\n"):
            line_upper = line.strip().upper()

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

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def interactive_refinement(
        self,
        summary_text: str,
        refinement_type: str,
        context: str = ""
    ) -> str:
        """
        Interactive refinement: shorter, detailed, or focus on specific aspects.

        Args:
            summary_text: Current summary
            refinement_type: "shorter", "detailed", "focus_methods", "focus_results"
            context: Additional context for focus
        """
        prompts = {
            "shorter": f"""
Make this summary significantly shorter (50% reduction) while keeping the most critical information:

{summary_text}

Shortened version:
""",
            "detailed": f"""
Expand this summary with more details, examples, and explanations:

{summary_text}

Detailed version:
""",
            "focus_methods": f"""
Rewrite this summary with heavy focus on methodology, approach, and technical details:

{summary_text}

Method-focused version:
""",
            "focus_results": f"""
Rewrite this summary emphasizing results, outcomes, and key findings:

{summary_text}

Results-focused version:
""",
            "focus_custom": f"""
Rewrite this summary with focus on: {context}

{summary_text}

Focused version:
"""
        }

        prompt = prompts.get(refinement_type, prompts["shorter"])

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return summary_text

# Global instance
advanced_summarizer = AdvancedSummarizationService()
