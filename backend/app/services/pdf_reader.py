import fitz  # PyMuPDF
from typing import List
import io


class PDFReader:
    """
    Extract text content from PDF files using PyMuPDF
    """

    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extract text from a single PDF file

        Args:
            file_content: PDF file content as bytes

        Returns:
            Extracted text as string
        """
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=file_content, filetype="pdf")

            text_content = []

            # Iterate through pages
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text = page.get_text()

                if text.strip():  # Only add non-empty pages
                    text_content.append(text)

            pdf_document.close()

            # Join all pages with double newline
            full_text = "\n\n".join(text_content)

            return full_text.strip()

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def extract_text_from_multiple_pdfs(files_content: List[tuple]) -> tuple:
        """
        Extract text from multiple PDF files

        Args:
            files_content: List of tuples (filename, file_bytes)

        Returns:
            Tuple of (combined_text, list_of_filenames)
        """
        all_texts = []
        file_names = []

        for filename, file_bytes in files_content:
            try:
                text = PDFReader.extract_text_from_pdf(file_bytes)
                if text:
                    all_texts.append(f"--- Content from {filename} ---\n{text}")
                    file_names.append(filename)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

        # Combine all texts
        combined_text = "\n\n".join(all_texts)

        return combined_text, file_names

    @staticmethod
    def chunk_text(text: str, max_length: int = 3000) -> List[str]:
        """
        Split text into chunks if it exceeds max_length

        Args:
            text: Input text
            max_length: Maximum length per chunk

        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]

        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks