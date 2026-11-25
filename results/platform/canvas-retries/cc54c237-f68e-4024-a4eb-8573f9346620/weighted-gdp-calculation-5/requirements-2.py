import json
import openpyxl
from openpyxl.utils import get_column_letter
import os
import re

def find_workbook_path(root_dir):
    """Find the first .xlsx file in the root directory."""
    for filename in os.listdir(root_dir):
        if filename.endswith('.xlsx') and not filename.startswith('~'):
            return os.path.join(root_dir, filename)
    return None

def is_year_header(value):
    """Check if a cell value represents a year header."""
    if value is None:
        return False
    if isinstance(value, (int, float)):
        # Check if it's a 4-digit year (e.g., 2023, 2024)
        if 1900 <= int(value) <= 2100:
            return True
    if isinstance(value, str):
        # Check for string years like "2023", "FY2023", "Year 2023"
        match = re.search(r'(19|20)\d{2}', value)
        if match:
            return True
    return False

def find_year_headers(ws):
    """Find all year headers in the worksheet and return their coordinates."""
    year_coords = []
    
    # Scan through all cells in the worksheet
    for row in ws.iter_rows():
        for cell in row:
            if is_year_header(cell.value):
                col_letter = get_column_letter(cell.column)
                coord = f"{col_letter}{cell.row}"
                year_coords.append({
                    "coordinate": coord,
                    "value": str(cell.value),
                    "row": cell.row,
                    "column": cell.column
                })
    
    return year_coords

def main():
    root_dir = "/root"
    workbook_path = find_workbook_path(root_dir)
    
    if not workbook_path:
        print(json.dumps({"error": "No Excel workbook found in /root"}))
        return
    
    wb = openpyxl.load_workbook(workbook_path, data_only=True)
    
    result = {
        "workbook": os.path.basename(workbook_path),
        "sheets": [],
        "year_headers_by_sheet": {}
    }
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Add sheet name to list
        result["sheets"].append(sheet_name)
        
        # Find year headers in this sheet
        year_headers = find_year_headers(ws)
        
        if year_headers:
            result["year_headers_by_sheet"][sheet_name] = year_headers
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
