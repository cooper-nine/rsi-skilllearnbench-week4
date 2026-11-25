import json
import os
from openpyxl import load_workbook

def find_populated_year_headers(ws):
    """
    Scans the worksheet for headers that look like years (e.g., 2023, 2024).
    Returns a list of dictionaries with coordinate and value.
    """
    year_headers = []
    
    # Iterate through all cells in the used range
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            if cell.value is None:
                continue
            
            val = str(cell.value).strip()
            
            # Check if the value is a 4-digit year
            if val.isdigit() and len(val) == 4:
                year_int = int(val)
                if 1900 <= year_int <= 2100:
                    year_headers.append({
                        "coordinate": cell.coordinate,
                        "value": val
                    })
    
    return year_headers

def main():
    # Locate the Excel file in the container
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
        result = {}
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            headers = find_populated_year_headers(ws)
            
            # Only include sheets that actually have year headers
            if headers:
                result[sheet_name] = {
                    "year_headers": headers
                }
        
        # If no years found anywhere, still return the structure but empty or indicate none
        if not result:
            # Fallback: just list sheets if no specific years found, but task asks for populated year headers
            # We will return an empty object or a message if strictly no years found.
            # However, usually these tasks imply years exist. Let's return what we found.
            pass
            
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()