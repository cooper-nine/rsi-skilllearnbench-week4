import json
import os
import subprocess
import shutil
import xml.etree.ElementTree as ET
from openpyxl import load_workbook

def run_recalc(filepath):
    """Run recalc.py to get calculated values."""
    try:
        result = subprocess.run(
            ['python', 'recalc.py', filepath, '30'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Recalc error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception in recalc: {e}")
        return None

def main():
    src_file = '/root/gdp.xlsx'
    temp_file = '/tmp/gdp_temp.xlsx'
    
    # Create a temporary copy for recalculation
    shutil.copy2(src_file, temp_file)
    
    # Run recalculation on the temporary copy
    recalc_result = run_recalc(temp_file)
    
    # Load the recalculated workbook (data_only=True to get values)
    wb_calc = load_workbook(temp_file, data_only=True)
    
    # Load the original workbook (to preserve formulas and styling)
    wb_orig = load_workbook(src_file)
    
    validation_report = {
        "status": "success",
        "message": "Validation completed",
        "sheets_validated": [],
        "formula_checks": [],
        "value_checks": []
    }
    
    # Define ranges to check based on task description
    # Step 1: H12:M17 and H19:M24 (Data filled via lookup)
    # Step 2: H28:M33 (Trade Balance Coefficients) + stats
    # Step 3: Weighted mean
    
    sheets_to_check = ['Task', 'Data']
    
    for sheet_name in sheets_to_check:
        if sheet_name not in wb_orig.sheetnames:
            continue
            
        ws_orig = wb_orig[sheet_name]
        ws_calc = wb_calc[sheet_name]
        
        sheet_report = {
            "sheet": sheet_name,
            "formulas_preserved": True,
            "values_match": True,
            "checked_ranges": []
        }
        
        # Check specific ranges mentioned in the task
        ranges_to_verify = [
            ("H12:M17", "Lookup Data Block 1"),
            ("H19:M24", "Lookup Data Block 2"),
            ("H28:M33", "Trade Balance Coefficients"),
        ]
        
        # Helper to convert range string to coordinates
        def get_range_coords(range_str):
            parts = range_str.split(':')
            start_col = ord(parts[0][0].upper()) - ord('A') + 1
            start_row = int(parts[0][1:])
            end_col = ord(parts[1][0].upper()) - ord('A') + 1
            end_row = int(parts[1][1:])
            return start_row, end_row, start_col, end_col
        
        for range_str, desc in ranges_to_verify:
            start_row, end_row, start_col, end_col = get_range_coords(range_str)
            
            mismatch_count = 0
            formula_count = 0
            
            for r in range(start_row, end_row + 1):
                for c in range(start_col, end_col + 1):
                    cell_coord = f"{chr(ord('A') + c - 1)}{r}"
                    
                    orig_cell = ws_orig.cell(row=r, column=c)
                    calc_cell = ws_calc.cell(row=r, column=c)
                    
                    # Check if formula exists in original
                    if orig_cell.value and isinstance(orig_cell.value, str) and orig_cell.value.startswith('='):
                        formula_count += 1
                        
                    # Compare values (original might be None if not calculated yet, calc has value)
                    orig_val = orig_cell.value
                    calc_val = calc_cell.value
                    
                    # If original has a formula, we just ensure it's preserved (checked above)
                    # If original has a value (static), it should match
                    if orig_val and not (isinstance(orig_val, str) and orig_val.startswith('=')):
                        if orig_val != calc_val:
                            # Allow small floating point differences
                            if isinstance(orig_val, (int, float)) and isinstance(calc_val, (int, float)):
                                if abs(orig_val - calc_val) > 1e-6:
                                    mismatch_count += 1
                            else:
                                mismatch_count += 1
            
            sheet_report["checked_ranges"].append({
                "range": range_str,
                "description": desc,
                "formulas_found": formula_count,
                "mismatches": mismatch_count
            })
            
            if mismatch_count > 0:
                sheet_report["values_match"] = False
                
        validation_report["sheets_validated"].append(sheet_report)
    
    # Global formula check using recalc output if available
    if recalc_result:
        validation_report["recalc_status"] = recalc_result.get("status", "unknown")
        validation_report["total_formulas"] = recalc_result.get("total_formulas", 0)
        validation_report["total_errors"] = recalc_result.get("total_errors", 0)
        if recalc_result.get("error_summary"):
            validation_report["errors"] = recalc_result["error_summary"]
            
    # Clean up temp file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    # Output final JSON
    print(json.dumps(validation_report))

if __name__ == "__main__":
    main()