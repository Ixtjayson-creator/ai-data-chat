import pandas as pd
import logging
from typing import Dict

def load_excel(file_path: str) -> str:
    """
    Loads an Excel file (.xlsx) from the given path and converts all sheets
    to a readable text format suitable for RAG processing.
    
    Args:
        file_path (str): The path to the Excel file.
        
    Returns:
        str: A concatenated string representation of all sheets in the Excel file.
    """
    try:
        # Load all sheets by setting sheet_name=None
        sheets_dict: Dict[str, pd.DataFrame] = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
        
        if not sheets_dict:
            return "The Excel file is empty."
            
        output_text = []
        
        for sheet_name, df in sheets_dict.items():
            if df.empty:
                continue
                
            # Add a header for each sheet to maintain context in RAG
            output_text.append(f"### [Excel Sheet: {sheet_name}]")
            
            # Convert each row into a structured record for better LLM comprehension
            for i, row in df.iterrows():
                record_lines = [f"#### Record {i+1} in {sheet_name}:"]
                for col in df.columns:
                    val = row[col]
                    record_lines.append(f"- {col}: {val}")
                output_text.append("\n".join(record_lines))
                output_text.append("") # Small spacer
            
            output_text.append("\n") # Larger spacer between sheets
            
        return "\n".join(output_text).strip() if output_text else "The Excel file contains no data."
        
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        logging.error(f"Failed to load Excel {file_path}: {e}")
        return f"Error processing Excel file: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(load_excel(sys.argv[1]))
    else:
        print("Usage: python excel_loader.py <path_to_excel>")
