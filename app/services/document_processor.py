import httpx
import PyPDF2
import io
import uuid
from typing import List, Dict, Any, Optional
from docx import Document as DocxDocument
from app.models.schemas import DocumentChunk
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing documents from URLs and extracting text content."""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    async def download_document(self, url: str) -> bytes:
        """Download document from URL using httpx."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Failed to download document from {url}: {str(e)}")
            raise Exception(f"Failed to download document: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text content from PDF bytes with validation."""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            # Clean and validate the extracted text
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text or len(cleaned_text.strip()) < 50:
                logger.warning("Extracted PDF text is too short or empty")
                return ""
            
            return cleaned_text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and validate extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        import re
        artifacts = [
            r'\b\d+\s*obj\b',  # PDF object references
            r'\bendobj\b',      # PDF end object markers
            r'\b<<\b',          # PDF dictionary markers
            r'\b>>\b',          # PDF dictionary end markers
            r'\b/F\s+\d+\b',    # PDF font references
            r'\b/Type\s+/[A-Za-z]+\b',  # PDF type references
            r'\b/Encoding\s+/[A-Za-z]+\b',  # PDF encoding references
            r'\b/Title\s*\([^)]*\)',  # PDF title markers
            r'\b/Author\s*\([^)]*\)',  # PDF author markers
            r'\b/Creator\s*\([^)]*\)',  # PDF creator markers
        ]
        
        for pattern in artifacts:
            text = re.sub(pattern, '', text)
        
        # Remove lines that are mostly special characters
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Check if line has meaningful content (not just symbols)
                alpha_chars = sum(1 for c in line if c.isalpha())
                total_chars = len(line)
                
                if total_chars > 0 and alpha_chars / total_chars > 0.3:
                    cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_text_from_docx(self, docx_bytes: bytes) -> str:
        """Extract text content from DOCX bytes."""
        try:
            docx_file = io.BytesIO(docx_bytes)
            doc = DocxDocument(docx_file)
            text = ""
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {str(e)}")
            raise Exception(f"Failed to parse DOCX: {str(e)}")
    
    def extract_text_from_email(self, email_content: str) -> str:
        """Extract text content from email (HTML/text)."""
        try:
            # Simple text extraction - in production, use proper HTML parsing
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', email_content)
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from email: {str(e)}")
            raise Exception(f"Failed to parse email: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[DocumentChunk]:
        """Split text into overlapping chunks for better context."""
        if chunk_size is None:
            chunk_size = self.chunk_size
        if overlap is None:
            overlap = self.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    content=chunk_text,
                    metadata={
                        "start_pos": start,
                        "end_pos": end,
                        "chunk_size": len(chunk_text),
                        "chunk_index": len(chunks)
                    }
                )
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - overlap)
        
        return chunks
    
    def extract_metadata(self, text: str, doc_type: str, url: str) -> Dict[str, Any]:
        """Extract metadata from document content."""
        metadata = {
            "doc_type": doc_type,
            "url": url,
            "total_length": len(text),
            "word_count": len(text.split()),
            "estimated_pages": len(text) // 2000,  # Rough estimate
        }
        
        # Extract potential document sections
        lines = text.split('\n')
        sections = []
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and line.isupper():
                # Potential section header
                if current_section:
                    sections.append(current_section)
                current_section = line
            elif line:
                current_section += " " + line
        
        if current_section:
            sections.append(current_section)
        
        metadata["sections"] = sections[:10]  # Limit to first 10 sections
        
        return metadata
    
    async def process_document(self, url: str) -> List[DocumentChunk]:
        """Main method to process a document from URL."""
        try:
            # Download document
            content_bytes = await self.download_document(url)
            
            # Determine document type and extract text
            if url.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(content_bytes)
                doc_type = "pdf"
            elif url.lower().endswith(('.docx', '.doc')):
                text = self.extract_text_from_docx(content_bytes)
                doc_type = "docx"
            else:
                # Assume it's text/email content
                text = content_bytes.decode('utf-8', errors='ignore')
                doc_type = "text"
            
            # Extract metadata
            metadata = self.extract_metadata(text, doc_type, url)
            
            # Create chunks
            chunks = self.chunk_text(text)
            
            # Add metadata to each chunk
            for chunk in chunks:
                chunk.metadata.update(metadata)
            
            logger.info(f"Processed document {url}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process document {url}: {str(e)}")
            raise Exception(f"Document processing failed: {str(e)}") 