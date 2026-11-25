import json
import openpyxl

# Load the workbook
wb = openpyxl.load_workbook('/root/gdp.xlsx')
ws = wb['Task']

# Fix H43:M43: Weighted Mean Formula
# Numerator: SUMPRODUCT(Exports, Weights) + SUMPRODUCT(Imports, Weights)
# Denominator: SUM(Exports) + SUM(Imports)
# Ranges:
# Exports: H12:M12 (Row 12) -> Actually rows 12:17 are exports per country? 
# Re-reading prompt: "rows 28:33 are already-percent coefficients, 12:17 exports and 19:24 imports."
# The formula is for a specific column (e.g., Column H for first country).
# So for Column H:
# Exports range: H12:H17
# Imports range: H19:H24
# Weights are Total Trade Volume = Exports + Imports.
# Wait, the prompt says: "The numerator is the export SUMPRODUCT PLUS the import SUMPRODUCT, because the weights are total trade volume, exports PLUS imports."
# This phrasing is slightly ambiguous. Usually weighted mean = Sum(Value * Weight) / Sum(Weight).
# Here Value = Trade Balance Coefficient (H28:H33).
# Weight = Total Trade Volume (Exports + Imports).
# So Numerator should be SUMPRODUCT(Coefficients, Exports+Imports).
# But the prompt explicitly says: "The numerator is the export SUMPRODUCT PLUS the import SUMPRODUCT".
# And "reuse its three original, same-column six-country ranges: rows 28:33 ... 12:17 ... 19:24".
# Let's interpret the user's correction strictly:
# Numerator = SUMPRODUCT(Exports_Range, Coeff_Range) + SUMPRODUCT(Imports_Range, Coeff_Range)?
# OR Numerator = SUMPRODUCT(Exports_Range, ???) + ...
# Let's re-read carefully: "The weighted formulas in H43:M43 currently produce #VALUE! because they pass a sum of two cell ranges to SUMPRODUCT and SUM."
# Original bad formula likely: =SUMPRODUCT(H28:H33, H12:H17+H19:H24) / SUM(H12:H17+H19:H24) -> This causes #VALUE in some Excel versions if not array entered or handled wrong.
# User instruction: "The numerator is the export SUMPRODUCT PLUS the import SUMPRODUCT... The denominator is SUM(exports) PLUS SUM(imports)."
# This implies:
# Num = SUMPRODUCT(H12:H17, H28:H33) + SUMPRODUCT(H19:H24, H28:H33)
# Den = SUM(H12:H17) + SUM(H19:H24)
# Result = ROUND(Num / Den, 1)
# Let's construct this formula for H43.
# Ranges for Col H:
# Coeffs: H28:H33
# Exports: H12:H17
# Imports: H19:H24

formula_h43 = "=ROUND((SUMPRODUCT(H12:H17,H28:H33)+SUMPRODUCT(H19:H24,H28:H33))/(SUM(H12:H17)+SUM(H19:H24)),1)"

# Apply to H43:M43
cols = ['H', 'I', 'J', 'K', 'L', 'M']
for col in cols:
    cell_coord = f"{col}43"
    # Adjust ranges dynamically based on column
    f = f"=ROUND((SUMPRODUCT({col}12:{col}17,{col}28:{col}33)+SUMPRODUCT({col}19:{col}24,{col}28:{col}33))/(SUM({col}12:{col}17)+SUM({col}19:{col}24)),1)"
    ws[cell_coord] = f

# Fix H39:M40: Replace PERCENTILE.INC with PERCENTILE
# Rows 39 and 40 contain percentiles.
# Assuming the formula is in these cells referencing H28:M33 or similar.
# We need to iterate H39:M40 and replace string "PERCENTILE.INC" with "PERCENTILE".
for row in [39, 40]:
    for col in cols:
        cell = ws[f"{col}{row}"]
        if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
            if 'PERCENTILE.INC' in cell.value:
                new_val = cell.value.replace('PERCENTILE.INC', 'PERCENTILE')
                ws[f"{col}{row}"] = new_val

# Set Task A1 to space if blank
if ws['A1'].value is None or ws['A1'].value == '':
    ws['A1'] = ' '

# Save
wb.save('/root/gdp.xlsx')

# Prepare output JSON
output = {
    "sheet_name": "Task",
    "formula_H43": ws['H43'].value,
    "formula_H39": ws['H39'].value
}

print(json.dumps(output))
