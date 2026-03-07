import pandas as pd
import logging
from typing import Optional

def load_csv(file_path: str) -> str:
    """
    Loads a CSV file from the given path and converts it to a readable text format
    suitable for RAG processing.
    
    Preserves column names and data rows while handling common encoding errors.
    
    Args:
        file_path (str): The absolute or relative path to the CSV file.
        
    Returns:
        str: A string representation of the CSV dataframe, or an error message if loading fails.
    """
    try:
        # Handle potential encoding issues (UTF-8 is standard, Latin-1 is common fallback)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except (UnicodeDecodeError, EOFError):
            df = pd.read_csv(file_path, encoding='latin-1')
            
        if df.empty:
            return ""

        # Convert to a readable string format preserving structure
        # index=False removes the row numbers which are usually irrelevant for RAG content
        return df.to_string(index=False)

    except FileNotFoundError:
        return f"Error: The file at {file_path} was not found."
    except Exception as e:
        logging.error(f"Error loading CSV {file_path}: {e}")
        return f"Error: An unexpected error occurred while reading {file_path}: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(load_csv(sys.argv[1]))
    else:
        print("Usage: python csv_loader.py <path_to_csv>")
