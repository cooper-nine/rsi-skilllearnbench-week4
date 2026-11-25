import json
import os
from openpyxl import load_workbook

def find_year_headers(ws):
    """
    Scans the worksheet for populated cells that look like year headers (e.g., 2023, 2024).
    Returns a list of dictionaries with coordinate and value.
    """
    year_headers = []
    # Iterate through all populated cells
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is None:
                continue
            
            val = cell.value
            # Check if value is an integer or string representing a 4-digit year
            is_year = False
            if isinstance(val, int):
                if 1900 <= val <= 2100:
                    is_year = True
            elif isinstance(val, str):
                # Try to parse string as integer year
                try:
                    year_int = int(val.strip())
                    if 1900 <= year_int <= 2100:
                        is_year = True
                except ValueError:
                    pass
            
            if is_year:
                year_headers.append({
                    "coordinate": cell.coordinate,
                    "value": str(val) # Store as string for JSON consistency
                })
    
    return year_headers

def main():
    # Locate the Excel file in the container root
    root_path = "/root"
    excel_file = None
    
    for f in os.listdir(root_path):
        if f.endswith(('.xlsx', '.xlsm')) and not f.startswith('~'):
            excel_file = os.path.join(root_path, f)
            break
    
    if not excel_file:
        print(json.dumps({"error": "No Excel file found in /root"}))
        return

    try:
        wb = load_workbook(excel_file, data_only=True)
        result = {
            "file": os.path.basename(excel_file),
            "sheets": []
        }
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            years = find_year_headers(ws)
            
            # Only include sheet if it has year headers or just list all sheets?
            # Task says: "Read only worksheet names and actual populated year headers"
            # We will list the sheet and whatever headers were found.
            sheet_info = {
                "name": sheet_name,
                "year_headers": years
            }
            result["sheets"].append(sheet_info)
            
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()