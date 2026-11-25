import json
from openpyxl import load_workbook

wb_path = "/root/gdp.xlsx"
wb = load_workbook(wb_path)
ws = wb["Task"]

# Ensure A1 has a space if blank to preserve coordinates on CSV export
if ws["A1"].value is None or ws["A1"].value == "":
    ws["A1"] = " "

# Fix H43:M43: Weighted Mean Formula
# Original ranges: Coefficients (28:33), Exports (12:17), Imports (19:24)
# Correct formula structure: ROUND(100 * (SUMPRODUCT(Coeff, Exp) - SUMPRODUCT(Coeff, Imp)) / (SUM(Exp) + SUM(Imp)), 1)
# We need to construct this for columns H to M (col indices 8 to 13)

for col in range(8, 14):  # H=8, I=9, J=10, K=11, L=12, M=13
    cell_coord = ws.cell(row=43, column=col).coordinate
    
    # Build ranges dynamically based on column
    # Coefficients: Row 28-33, current col
    coeff_range = f"{ws.cell(row=28, column=col).coordinate}:{ws.cell(row=33, column=col).coordinate}"
    # Exports: Row 12-17, current col
    exp_range = f"{ws.cell(row=12, column=col).coordinate}:{ws.cell(row=17, column=col).coordinate}"
    # Imports: Row 19-24, current col
    imp_range = f"{ws.cell(row=19, column=col).coordinate}:{ws.cell(row=24, column=col).coordinate}"
    
    # Construct the corrected formula
    # SUMPRODUCT(Coeff, Exp) - SUMPRODUCT(Coeff, Imp) divided by SUM(Exp) + SUM(Imp)
    # Multiplied by 100 and rounded to 1 decimal
    formula = f'=ROUND(100*(SUMPRODUCT({coeff_range},{exp_range})-SUMPRODUCT({coeff_range},{imp_range}))/(SUM({exp_range})+SUM({imp_range})),1)'
    
    ws[cell_coord] = formula

# Replace PERCENTILE.INC with legacy PERCENTILE in H39:M40
for row in [39, 40]:
    for col in range(8, 14):
        cell = ws.cell(row=row, column=col)
        if cell.value and isinstance(cell.value, str) and "PERCENTILE.INC" in cell.value:
            old_formula = cell.value
            new_formula = old_formula.replace("PERCENTILE.INC", "PERCENTILE")
            cell.value = new_formula

wb.save(wb_path)
wb.close()

# Prepare output JSON
output = {
    "sheet_name": "Task",
    "formula_H43": ws["H43"].value,
    "formula_H39": ws["H39"].value
}

print(json.dumps(output))
