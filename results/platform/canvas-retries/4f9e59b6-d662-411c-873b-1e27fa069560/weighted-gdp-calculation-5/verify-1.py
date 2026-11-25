import json
from openpyxl import load_workbook

wb_path = "gdp.xlsx"
wb = load_workbook(wb_path)
ws = wb["Task"]

# Ensure A1 is a space if blank to preserve coordinates on CSV export
if ws["A1"].value is None or ws["A1"].value == "":
    ws["A1"] = " "

# Fix H39:M40: Replace PERCENTILE.INC with legacy PERCENTILE
for col in range(8, 14):  # H=8 to M=13
    for row in [39, 40]:
        cell = ws.cell(row=row, column=col)
        if cell.value and isinstance(cell.value, str) and "PERCENTILE.INC" in cell.value:
            new_formula = cell.value.replace("PERCENTILE.INC", "PERCENTILE")
            cell.value = new_formula

# Fix H43:M43: Weighted Mean Formula
# Original ranges:
# Exports: Rows 12-17 (H12:H17 etc)
# Imports: Rows 19-24 (H19:H24 etc)
# Coefficients: Rows 28-33 (H28:H33 etc)
# Logic:
# Numerator = SUMPRODUCT(Exports, Coeff) + SUMPRODUCT(Imports, Coeff)
# Denominator = SUM(Exports) + SUM(Imports)
# Result = ROUND((Numerator / Denominator) * 100, 1) -- Wait, prompt says "earlier coefficient formulas already did both" (subtract and multiply by 100).
# Prompt: "Never subtract imports here or multiply by 100; the earlier coefficient formulas already did both."
# So Coeffs in 28:33 are already percentages (e.g. 12.3).
# Formula: ROUND( (SUMPRODUCT(Exp, Coeff) + SUMPRODUCT(Imp, Coeff)) / (SUM(Exp) + SUM(Imp)), 1 )

for col in range(8, 14):  # H to M
    col_letter = ws.cell(row=1, column=col).column_letter
    row = 43
    
    # Construct ranges for this column
    # Exports: col+12 to col+17 -> e.g., H12:H17
    # Imports: col+19 to col+24 -> e.g., H19:H24
    # Coeffs:  col+28 to col+33 -> e.g., H28:H33
    
    exp_range = f"{col_letter}12:{col_letter}17"
    imp_range = f"{col_letter}19:{col_letter}24"
    coeff_range = f"{col_letter}28:{col_letter}33"
    
    # Numerator: SUMPRODUCT(Exports, Coeffs) + SUMPRODUCT(Imports, Coeffs)
    numerator = f"SUMPRODUCT({exp_range},{coeff_range})+SUMPRODUCT({imp_range},{coeff_range})"
    
    # Denominator: SUM(Exports) + SUM(Imports)
    denominator = f"SUM({exp_range})+SUM({imp_range})"
    
    formula = f"ROUND(({numerator})/({denominator}),1)"
    ws.cell(row=row, column=col).value = formula

wb.save(wb_path)

result = {
    "sheet": "Task",
    "formula_H43": ws["H43"].value,
    "formula_H39": ws["H39"].value
}

print(json.dumps(result))
