import json
import subprocess
import shutil
import os
import re
from openpyxl import load_workbook

def run_validation():
    src_path = "/root/gdp.xlsx"
    temp_path = "/tmp/gdp_recalc.xlsx"
    
    # Copy original to temp for recalculation
    shutil.copy2(src_path, temp_path)
    
    # Run recalc.py on the temporary copy to get calculated values
    try:
        result = subprocess.run(
            ["python", "recalc.py", temp_path, "30"],
            capture_output=True,
            text=True,
            timeout=45
        )
        recalc_output = result.stdout
        try:
            recalc_data = json.loads(recalc_output)
        except json.JSONDecodeError:
            recalc_data = {"status": "unknown", "message": "Could not parse recalc output"}
    except Exception as e:
        recalc_data = {"status": "error", "message": str(e)}
    
    # Load the original workbook (preserving formulas and styles)
    wb_orig = load_workbook(src_path, data_only=False)
    
    # Load the recalculated workbook (to get numeric values)
    wb_recalc = load_workbook(temp_path, data_only=True)
    
    validation_result = {
        "status": "success",
        "message": "Validation completed",
        "formula_check": recalc_data,
        "data_verification": {}
    }
    
    # Verify specific ranges mentioned in task
    # Step 1 ranges: H12:L17, H19:L24, H26:L31
    # Step 2 ranges: H35:L40 + stats
    # Step 3: Weighted mean
    
    sheets_to_check = ["Task", "Data"]
    verified_cells = []
    
    for sheet_name in sheets_to_check:
        if sheet_name in wb_orig.sheetnames and sheet_name in wb_recalc.sheetnames:
            ws_orig = wb_orig[sheet_name]
            ws_recalc = wb_recalc[sheet_name]
            
            # Check a sample of cells in the target ranges to ensure formulas exist and values are populated
            # Ranges: H12:L17 (rows 12-17, cols 8-12)
            sample_coords = [
                (12, 8), (12, 12), (17, 8), (17, 12),
                (19, 8), (24, 12),
                (26, 8), (31, 12),
                (35, 8), (40, 12),
                (42, 8), (42, 12) # Assuming stats are below row 40
            ]
            
            for row, col in sample_coords:
                cell_coord = f"{chr(64+col)}{row}" # Simple conversion for H-L
                if col > 26: 
                    # Handle columns beyond Z if necessary, though H-L is within A-Z
                    pass
                
                orig_cell = ws_orig.cell(row=row, column=col)
                recalc_cell = ws_recalc.cell(row=row, column=col)
                
                has_formula = orig_cell.value is not None and isinstance(orig_cell.value, str) and '=' in str(orig_cell.value)
                has_value = recalc_cell.value is not None
                
                verified_cells.append({
                    "sheet": sheet_name,
                    "cell": cell_coord,
                    "has_formula": has_formula,
                    "has_calculated_value": has_value,
                    "value": recalc_cell.value
                })
    
    validation_result["data_verification"]["sampled_cells"] = verified_cells
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    print(json.dumps(validation_result))

if __name__ == "__main__":
    run_validation()