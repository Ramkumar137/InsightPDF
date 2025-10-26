"""
PDF text extraction service using PyPDF2 and pdfplumber
UPGRADED: Better text extraction with fallback mechanisms
"""
import PyPDF2
import pdfplumber
from typing import List, Dict
from fastapi import UploadFile, HTTPException
import io

class PDFReader:
    """Enhanced PDF text extraction with multiple methods"""
    
    @staticmethod
    async def extract_text_from_pdf(file: UploadFile) -> str:
        """
        Extract text from PDF using PyPDF2 with pdfplumber fallback.
        
        Args:
            file: UploadFile object from FastAPI
            
        Returns:
            Extracted text as string
        """
        try:
            # Read file content
            content = await file.read()
            
            # Try PyPDF2 first (faster)
            try:
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                text_content = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
                
                full_text = "\n\n".join(text_content)
                
                # If PyPDF2 got good content, use it
                if len(full_text.strip()) > 100:
                    return full_text.strip()
                
            except Exception as e:
                print(f"PyPDF2 failed, trying pdfplumber: {e}")
            
            # Fallback to pdfplumber (more robust for complex PDFs)
            pdf_file = io.BytesIO(content)
            text_content = []
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                raise ValueError("No text content found in PDF")
            
            return full_text.strip()
            
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
    async def extract_text_from_multiple_pdfs(files: List[UploadFile]) -> Dict:
        """
        Extract text from multiple PDF files.
        
        Args:
            files: List of UploadFile objects
            
        Returns:
            Dictionary with combined text and metadata
        """
        file_texts = {}
        all_text = []
        total_pages = 0
        
        for file in files:
            text = await PDFReader.extract_text_from_pdf(file)
            file_texts[file.filename] = text
            all_text.append(f"=== Document: {file.filename} ===\n\n{text}")
            
            # Count pages for metadata
            await file.seek(0)
            content = await file.read()
            try:
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages += len(pdf_reader.pages)
            except:
                pass
        
        combined_text = "\n\n" + "="*50 + "\n\n".join(all_text)
        
        return {
            "combined_text": combined_text,
            "individual_files": file_texts,
            "file_names": [f.filename for f in files],
            "total_pages": total_pages,
            "total_chars": len(combined_text)
        }
    
    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 30000) -> List[str]:
        """
        Split text into chunks for processing.
        
        Args:
            text: Input text
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs
        paragraphs = text.split("\n\n")
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks