import json
import os
from openpyxl import load_workbook

def find_year_headers(ws):
    """
    Scans the first 10 rows of the worksheet to find headers that look like years (e.g., 2023, 2024).
    Returns a list of dictionaries with coordinate and value.
    """
    headers = []
    # Scan first 10 rows and first 50 columns for potential year headers
    for row in ws.iter_rows(min_row=1, max_row=10, max_col=50, values_only=True):
        for col_idx, cell_value in enumerate(row, start=1):
            if cell_value is None:
                continue
            
            # Check if value is an integer representing a year (1900-2100)
            if isinstance(cell_value, int) and 1900 <= cell_value <= 2100:
                col_letter = openpyxl.utils.get_column_letter(col_idx)
                # Find the actual row number by iterating again since iter_rows(values_only) loses row index context easily without enumeration
                # Re-scan specifically for this row to get exact coordinate if needed, but we can track row index in the loop
                pass 
            
    # Better approach: Iterate with row index
    found_years = []
    for r_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, max_col=50), start=1):
        for cell in row:
            val = cell.value
            if val is not None:
                # Check for integer year
                if isinstance(val, int) and 1900 <= val <= 2100:
                    found_years.append({
                        "coordinate": cell.coordinate,
                        "value": val
                    })
                # Check for string year (sometimes formatted as text)
                elif isinstance(val, str) and val.isdigit() and 1900 <= int(val) <= 2100:
                    found_years.append({
                        "coordinate": cell.coordinate,
                        "value": int(val)
                    })
    return found_years

# Locate the Excel file in /root
root_path = "/root"
excel_file = None

for f in os.listdir(root_path):
    if f.endswith(('.xlsx', '.xlsm')):
        excel_file = os.path.join(root_path, f)
        break

if not excel_file:
    print(json.dumps({"error": "No Excel file found in /root"}))
else:
    wb = load_workbook(excel_file, data_only=True)
    result = {
        "file": os.path.basename(excel_file),
        "sheets": []
    }
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        year_headers = find_year_headers(ws)
        
        sheet_info = {
            "name": sheet_name
        }
        
        if year_headers:
            sheet_info["year_headers"] = year_headers
            
        result["sheets"].append(sheet_info)

    print(json.dumps(result))