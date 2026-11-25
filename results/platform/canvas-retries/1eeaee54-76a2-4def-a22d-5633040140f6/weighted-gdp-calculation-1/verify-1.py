import json
import os
import subprocess
import tempfile
from openpyxl import load_workbook

def main():
    wb_path = "/root/gdp.xlsx"
    
    # Load workbook preserving formulas and styling
    wb = load_workbook(wb_path)
    ws = wb.active
    
    # Check A1 for empty state to preserve coordinate origin on CSV export
    if ws.cell(row=1, column=1).value is None:
        ws.cell(row=1, column=1).value = " "
    
    # Replace incompatible QUARTILE.INC and PERCENTILE.INC with legacy equivalents
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                formula = cell.value
                original_formula = formula
                # Replace QUARTILE.INC with QUARTILE
                formula = formula.replace("QUARTILE.INC(", "QUARTILE(")
                # Replace PERCENTILE.INC with PERCENTILE
                formula = formula.replace("PERCENTILE.INC(", "PERCENTILE(")
                
                if formula != original_formula:
                    cell.value = formula
    
    # Save the modified workbook
    wb.save(wb_path)
    
    # Recalculate using ssconvert to a temporary CSV to check for errors
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_csv:
        tmp_csv_path = tmp_csv.name
    
    try:
        # Use ssconvert to convert and implicitly check for basic structural integrity
        # Note: ssconvert (gnumeric) handles formula evaluation during export
        result = subprocess.run(
            ["ssconvert", wb_path, tmp_csv_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        error_check = "none"
        if result.returncode != 0:
            error_check = result.stderr.strip()
        elif "#REF!" in result.stderr or "#DIV/0!" in result.stderr:
            error_check = "Spreadsheet errors detected in stderr"
        else:
            # Double check by reading the CSV content for common error strings if ssconvert didn't fail
            try:
                with open(tmp_csv_path, 'r') as f:
                    content = f.read()
                    if "#REF!" in content or "#DIV/0!" in content or "#NAME?" in content:
                        error_check = "Formula errors found in exported CSV content"
                    else:
                        error_check = "clean"
            except Exception:
                error_check = "could_not_read_csv"
                
    except subprocess.TimeoutExpired:
        error_check = "timeout"
    except FileNotFoundError:
        error_check = "ssconvert_not_found"
    finally:
        if os.path.exists(tmp_csv_path):
            os.remove(tmp_csv_path)
    
    # Inspect cell A1 to confirm the whitespace fix
    wb_check = load_workbook(wb_path, data_only=False)
    ws_check = wb_check.active
    a1_value = ws_check.cell(row=1, column=1).value
    
    output = {
        "inspected_cell_A1": a1_value,
        "workbook_path": wb_path,
        "ssconvert_status": error_check,
        "formula_replacements_applied": True
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
