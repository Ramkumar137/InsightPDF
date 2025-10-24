"""
PDF text extraction service using PyMuPDF (fitz)
"""
import fitz  # PyMuPDF
from typing import List
from fastapi import UploadFile, HTTPException
import io

class PDFReader:
    """Service for extracting text from PDF files"""
    
    @staticmethod
    async def extract_text_from_pdf(file: UploadFile) -> str:
        """
        Extract text content from a single PDF file.
        
        Args:
            file: UploadFile object from FastAPI
            
        Returns:
            Extracted text as string
            
        Raises:
            HTTPException: If PDF cannot be processed
        """
        try:
            # Read file content
            content = await file.read()
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=content, filetype="pdf")
            
            # Extract text from all pages
            text_content = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text_content.append(page.get_text())
            
            # Close document
            pdf_document.close()
            
            # Combine all pages
            full_text = "\n\n".join(text_content)
            
            # Clean up extra whitespace
            full_text = " ".join(full_text.split())
            
            if not full_text.strip():
                raise ValueError("No text content found in PDF")
            
            return full_text
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "message": f"Failed to extract text from PDF: {str(e)}",
                        "code": "PDF_EXTRACTION_FAILED"
                    }
                }
            )
    
    @staticmethod
    async def extract_text_from_multiple_pdfs(files: List[UploadFile]) -> dict:
        """
        Extract text from multiple PDF files.
        
        Args:
            files: List of UploadFile objects
            
        Returns:
            Dictionary with combined text and individual file texts
        """
        file_texts = {}
        all_text = []
        
        for file in files:
            text = await PDFReader.extract_text_from_pdf(file)
            file_texts[file.filename] = text
            all_text.append(f"=== {file.filename} ===\n{text}")
        
        return {
            "combined_text": "\n\n".join(all_text),
            "individual_files": file_texts,
            "file_names": [f.filename for f in files]
        }
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 3000) -> str:
        """
        Truncate text to maximum length for model input.
        
        Args:
            text: Input text
            max_length: Maximum character length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        # Try to cut at a sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.8:  # If we're close enough to the limit
            return truncated[:last_period + 1]
        
        return truncated