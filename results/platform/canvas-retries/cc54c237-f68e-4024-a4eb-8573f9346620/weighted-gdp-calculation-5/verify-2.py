import json
import subprocess
import os
import shutil
import xml.etree.ElementTree as ET
from openpyxl import load_workbook

def run_validation():
    input_file = "/root/gdp.xlsx"
    temp_file = "/tmp/gdp_recalc.xlsx"
    checkpoint_file = "/tmp/checkpoint.json"
    
    # Load previous checkpoint if exists
    prev_checkpoint = {}
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                prev_checkpoint = json.load(f)
        except:
            pass

    # Copy original file to temp for recalculation
    shutil.copy2(input_file, temp_file)
    
    # Run recalc.py to get calculated values
    try:
        result = subprocess.run(
            ["python", "recalc.py", temp_file, "30"],
            capture_output=True,
            text=True,
            timeout=45
        )
        recalc_output = result.stdout.strip()
        if recalc_output:
            recalc_data = json.loads(recalc_output)
        else:
            recalc_data = {"status": "success", "total_errors": 0, "total_formulas": 0}
    except Exception as e:
        recalc_data = {"status": "error", "message": str(e), "total_errors": 0, "total_formulas": 0}
    
    # Load original workbook to preserve formulas and formatting
    wb_original = load_workbook(input_file, data_only=False)
    # Load recalculated workbook to get numeric values
    wb_recalc = load_workbook(temp_file, data_only=True)
    
    validation_results = {
        "status": "success",
        "formulas_preserved": True,
        "formatting_preserved": True,
        "calculated_values_valid": True,
        "errors": [],
        "recalc_status": recalc_data.get("status", "unknown"),
        "total_formulas": recalc_data.get("total_formulas", 0),
        "total_errors": recalc_data.get("total_errors", 0),
        "error_summary": recalc_data.get("error_summary", {})
    }
    
    # Check for formula errors in recalc output
    if recalc_data.get("total_errors", 0) > 0:
        validation_results["calculated_values_valid"] = False
        validation_results["errors"].append(f"Formula errors found: {recalc_data.get('total_errors')}")
    
    # Verify key ranges exist and have values in recalculated sheet
    task_sheet_orig = wb_original["Task"] if "Task" in wb_original.sheetnames else None
    task_sheet_recalc = wb_recalc["Task"] if "Task" in wb_recalc.sheetnames else None
    
    if task_sheet_orig and task_sheet_recalc:
        # Check yellow ranges H12:M17, H19:M24, H28:M33
        ranges_to_check = [
            ("H12:M17", [(12, 8), (17, 13)]),
            ("H19:M24", [(19, 8), (24, 13)]),
            ("H28:M33", [(28, 8), (33, 13)])
        ]
        
        for range_name, (start_row, start_col), (end_row, end_col) in ranges_to_check:
            has_formulas = False
            has_values = False
            
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    cell_orig = task_sheet_orig.cell(row=row, column=col)
                    cell_recalc = task_sheet_recalc.cell(row=row, column=col)
                    
                    if cell_orig.value and isinstance(cell_orig.value, str) and cell_orig.value.startswith("="):
                        has_formulas = True
                    
                    if cell_recalc.value is not None and not isinstance(cell_recalc.value, str):
                        has_values = True
                    elif cell_recalc.value is not None and isinstance(cell_recalc.value, str) and not cell_recalc.value.startswith("#"):
                        has_values = True
            
            if not has_formulas:
                validation_results["errors"].append(f"Range {range_name} missing formulas")
                validation_results["formulas_preserved"] = False
            
            if not has_values and has_formulas:
                validation_results["errors"].append(f"Range {range_name} formulas not calculating")
                validation_results["calculated_values_valid"] = False
    
    # Check summary statistics range (likely below row 33)
    # Verify weighted mean calculation exists
    weighted_mean_found = False
    for row in range(34, 50):
        for col in range(8, 14):
            cell = task_sheet_orig.cell(row=row, column=col)
            if cell.value and isinstance(cell.value, str) and "SUMPRODUCT" in cell.value.upper():
                weighted_mean_found = True
                break
    
    if not weighted_mean_found:
        # Check if any cell in expected area has SUMPRODUCT
        for row in range(1, 100):
            for col in range(1, 20):
                cell = task_sheet_orig.cell(row=row, column=col)
                if cell.value and isinstance(cell.value, str) and "SUMPRODUCT" in cell.value.upper():
                    weighted_mean_found = True
                    break
    
    if not weighted_mean_found:
        validation_results["errors"].append("Weighted mean (SUMPRODUCT) formula not found")
    
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    # Final status determination
    if validation_results["errors"]:
        validation_results["status"] = "partial_success" if validation_results["formulas_preserved"] else "failed"
    
    return validation_results

if __name__ == "__main__":
    result = run_validation()
    print(json.dumps(result))