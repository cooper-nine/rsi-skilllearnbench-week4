import json
import openpyxl

wb = openpyxl.load_workbook('/root/gdp.xlsx', data_only=False)
sheet_names = wb.sheetnames
task_sheet = wb['Task']
data_sheet = wb['Data']

formula_samples = []

# Scan Task sheet for formulas in the expected yellow ranges
ranges_to_check = [
    "H12:M17",
    "H19:M24",
    "H28:M33"
]

for range_str in ranges_to_check:
    start_col, end_col = range_str.split(':')[0][0], range_str.split(':')[1][0]
    start_row, end_row = int(range_str.split(':')[0][1:]), int(range_str.split(':')[1][1:])
    
    col_start_idx = ord(start_col) - ord('A') + 1
    col_end_idx = ord(end_col) - ord('A') + 1
    
    for row in range(start_row, end_row + 1):
        for col in range(col_start_idx, col_end_idx + 1):
            cell = task_sheet.cell(row=row, column=col)
            if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                coord = cell.coordinate
                formula_samples.append({"coordinate": f"Task!{coord}", "formula": cell.value})
                if len(formula_samples) >= 5:
                    break
        if len(formula_samples) >= 5:
            break
    if len(formula_samples) >= 5:
        break

result = {
    "sheet_names": sheet_names,
    "formula_samples": formula_samples[:5]
}

print(json.dumps(result))