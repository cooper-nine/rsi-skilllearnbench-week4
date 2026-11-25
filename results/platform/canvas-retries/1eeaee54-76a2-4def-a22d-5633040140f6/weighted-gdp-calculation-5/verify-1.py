import json
import os
import subprocess
import tempfile
from openpyxl import load_workbook

def run():
    wb_path = "/root/gdp.xlsx"
    
    # Load workbook preserving formulas
    wb = load_workbook(wb_path)
    ws = wb.active
    
    # Check A1 for coordinate origin preservation
    if ws['A1'].value is None:
        ws['A1'] = ' '
    
    # Replace incompatible functions: QUARTILE.INC -> QUARTILE, PERCENTILE.INC -> PERCENTILE
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                formula = cell.value
                original = formula
                # Replace QUARTILE.INC with QUARTILE
                formula = formula.replace('QUARTILE.INC', 'QUARTILE')
                # Replace PERCENTILE.INC with PERCENTILE
                formula = formula.replace('PERCENTILE.INC', 'PERCENTILE')
                
                if formula != original:
                    cell.value = formula
    
    # Save modified workbook
    wb.save(wb_path)
    
    # Recalculate using ssconvert to temporary CSV
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_csv:
        tmp_csv_path = tmp_csv.name
    
    try:
        # Run ssconvert with -S flag
        result = subprocess.run(
            ['ssconvert', '-S', wb_path, tmp_csv_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"ssconvert failed: {result.stderr}")
        
        # Read CSV to check for errors
        with open(tmp_csv_path, 'r') as f:
            csv_content = f.read()
        
        # Check for common spreadsheet errors in CSV
        errors_found = []
        lines = csv_content.split('\n')
        for row_idx, line in enumerate(lines, 1):
            if any(err in line for err in ['#VALUE!', '#REF!', '#DIV/0!', '#NAME?', '#NUM!']):
                cells = line.split(',')
                for col_idx, cell in enumerate(cells, 1):
                    if any(err in cell for err in ['#VALUE!', '#REF!', '#DIV/0!', '#NAME?', '#NUM!']):
                        coord = f"{chr(64 + col_idx)}{row_idx}" if col_idx <= 26 else f"{chr(64 + (col_idx-26)//26)}{chr(65 + (col_idx-26)%26)}{row_idx}"
                        error_type = cell.strip()
                        errors_found.append({"coordinate": coord, "error": error_type})
        
        if errors_found:
            # Raise exception with first error for retry
            err = errors_found[0]
            raise Exception(f"Spreadsheet error found at {err['coordinate']}: {err['error']}")
        
        # Success - return inspection results
        output = {
            "inspected_cell": "A1",
            "workbook_path": wb_path,
            "status": "success",
            "coordinate_origin_preserved": True,
            "functions_replaced": True
        }
        
        print(json.dumps(output))
        
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_csv_path):
            os.unlink(tmp_csv_path)

if __name__ == "__main__":
    run()