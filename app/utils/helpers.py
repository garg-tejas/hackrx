import re
import hashlib
from typing import List, Dict, Any
from datetime import datetime

def sanitize_text(text: str) -> str:
    """Sanitize text by removing extra whitespace and special characters."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
    
    return text.strip()

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text using simple frequency analysis."""
    if not text:
        return []
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_keywords[:max_keywords]]

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity using Jaccard similarity."""
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def generate_chunk_id(content: str, metadata: Dict[str, Any]) -> str:
    """Generate a unique ID for a document chunk."""
    # Create a hash from content and metadata
    hash_input = f"{content[:100]}{str(metadata)}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def format_timestamp() -> str:
    """Format current timestamp for logging."""
    return datetime.utcnow().isoformat()

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def extract_sections(text: str) -> List[Dict[str, str]]:
    """Extract potential document sections from text."""
    sections = []
    lines = text.split('\n')
    current_section = ""
    current_title = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line might be a section header (all caps, short, ends with colon)
        if (line.isupper() and len(line) < 100 and 
            (line.endswith(':') or line.endswith('.') or len(line.split()) <= 5)):
            # Save previous section
            if current_section:
                sections.append({
                    "title": current_title,
                    "content": current_section.strip()
                })
            
            # Start new section
            current_title = line
            current_section = ""
        else:
            current_section += line + "\n"
    
    # Add the last section
    if current_section:
        sections.append({
            "title": current_title,
            "content": current_section.strip()
        })
    
    return sections

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url)) 