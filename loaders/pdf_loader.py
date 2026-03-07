import logging
import re
from pdfminer.high_level import extract_text

def load_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfminer.six and cleans extra whitespace.
    
    Args:
        file_path (str): The path to the PDF file.
        
    Returns:
        str: Cleaned plain text extracted from the PDF.
    """
    try:
        # Extract text from PDF
        text = extract_text(file_path)
        
        if not text:
            return ""
            
        # Clean extra whitespace
        # 1. Replace multiple newlines with single newlines
        text = re.sub(r'\n+', '\n', text)
        # 2. Replace multiple spaces with single spaces
        text = re.sub(r' +', ' ', text)
        # 3. Strip leading/trailing whitespace
        text = text.strip()
        
        return text
        
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        logging.error(f"Failed to load PDF {file_path}: {e}")
        return f"Error processing PDF file: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(load_pdf(sys.argv[1]))
    else:
        print("Usage: python pdf_loader.py <path_to_pdf>")
