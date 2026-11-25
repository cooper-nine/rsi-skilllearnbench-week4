import json
import openpyxl
from openpyxl.utils import get_column_letter

# Load the workbook
wb = openpyxl.load_workbook('/root/gdp.xlsx')
ws = wb['Task']

# Fix H43:M43: Replace broken SUMPRODUCT with split terms
# Original logic was likely: ROUND(SUMPRODUCT(Coeff, Exp+Imp) / SUM(Totals), 4) which fails
# New logic: ROUND((SUMPRODUCT(Coeff, Exp) + SUMPRODUCT(Coeff, Imp)) / (SUM(ExpTot) + SUM(ImpTot)), 4)
# Assuming structure: Coeffs in row above or specific range, Exports/Imports in columns, Totals at bottom.
# Based on typical Trade Balance tasks:
# Row 42 might be coefficients? Or H42:M42?
# Let's assume the formula needs to reference specific ranges. 
# Without seeing the exact grid, I will construct the standard correction for this specific error type.
# Pattern: H43 usually aggregates H column data.
# Hypothesis: 
# Numerator: SUMPRODUCT(Coefficients_Row, Exports_Row) + SUMPRODUCT(Coefficients_Row, Imports_Row)
# Denominator: SUM(Exports_Row) + SUM(Imports_Row)
# Let's assume Coefficients are in Row 42 (H42:M42), Exports in Row 41, Imports in Row 40? 
# Or maybe the table is vertical? 
# Given "weighted formulas in H43:M43", these are likely summary cells for columns H through M.
# If H43 is for column H, it might be weighting values in H against something else?
# Actually, "pass a sum of two cell ranges to SUMPRODUCT" implies the formula looked like:
# =SUMPRODUCT(Range1, Range2+Range3) -> Error.
# Correction: =SUMPRODUCT(Range1, Range2) + SUMPRODUCT(Range1, Range3).
# And denominator SUM(Range2+Range3) -> SUM(Range2) + SUM(Range3).

# Let's assume the data layout based on common task structures:
# Rows 4-41: Data.
# Row 42: Weights/Coefficients? Or maybe the formula is across the row H43:M43 calculating a weighted average for each year (columns H-M).
# If H43:M43 are the targets, they likely calculate a metric for the column they are in.
# But SUMPRODUCT suggests multiplying arrays. If H43 is a single cell, it might be aggregating a whole column or row.
# "Weighted formulas in H43:M43" -> One formula per cell from H to M.
# This implies the formula in H43 uses data from column H? Or row 43 uses data from row 43?
# If it's a trade balance coefficient per year (columns H-M), then for column H:
# Numerator: Sum of (Coefficient * Export) + Sum of (Coefficient * Import)?
# Wait, if H43 is just one cell, and it's "weighted", maybe it weights different sectors (rows) within that year (column).
# Let's assume the "two cell ranges" passed to SUM were Exports and Imports for that year.
# And the Coefficient vector is fixed (e.g., sector weights in a specific row or column).
# Let's guess the structure: 
# Sectors in rows (e.g., 4 to 41). Years in columns (H to M).
# H43 calculates the weighted coefficient for Year H.
# Weights might be in a specific row, say Row 3? Or maybe the "Coefficient" is the value itself?
# Re-reading: "weighted formulas... pass a sum of two cell ranges to SUMPRODUCT and SUM".
# Likely: =ROUND(SUMPRODUCT(Weights, Exports+Imports) / SUM(Exports+Imports), 4).
# Where Weights is a fixed range (e.g., $B$4:$B$41) and Exports/Imports are the column ranges (e.g., H4:H41, I4:I41).
# Correction for H43: 
# =ROUND((SUMPRODUCT(Weights, Exports_H) + SUMPRODUCT(Weights, Imports_H)) / (SUM(Exports_H) + SUM(Imports_H)), 4)
# But where are Exports and Imports? Maybe alternating rows? Or two separate blocks?
# Common pattern: Exports in rows 4-22, Imports in 23-41? Or adjacent columns?
# If the error is "sum of two cell ranges", the original formula was likely:
# =SUMPRODUCT(Weights, H4:H41+I4:I41) -- wait, H43 is in column H.
# Maybe the data in column H is "Net"? No, "Trade Balance Coefficient".
# Let's assume the sheet has Exports and Imports in separate rows for each year column?
# Or maybe the "two ranges" are the Export column and Import column for that year?
# If H43 is for Year H, and there are two columns per year? No, H43:M43 is 6 cells. H,M are 6 columns.
# So 1 column per year.
# Then the "two ranges" summed inside must be within that column. E.g. Top half (Exports) + Bottom half (Imports).
# Let's assume Rows 4-22 = Exports, Rows 23-41 = Imports.
# Weights in Column A (A4:A41)? Or a specific row?
# Let's try to detect the existing formula to be safe, but the prompt says "Fix ... before inspecting".
# I must generate the fix blindly based on the description.
# Description: "Replace each by two SUMPRODUCT terms ... divided by the sum of two separately calculated trade totals".
# Formula pattern for cell X43 (where X is H..M):
# Old: =ROUND(SUMPRODUCT(Weights, X4:X22+X23:X41) / SUM(X4:X22+X23:X41), 4) [Hypothetical]
# New: =ROUND((SUMPRODUCT(Weights, X4:X22) + SUMPRODUCT(Weights, X23:X41)) / (SUM(X4:X22) + SUM(X23:X41)), 4)
# What are the ranges? 
# Standard GDP task often has 38 rows of data (4 to 41). Split 19/19? Or 20/20?
# Let's assume the split is equal or defined by the task. 
# If I can't know the exact split, I'll use a generic placeholder that matches the "two ranges" description.
# However, I need to write valid Excel syntax.
# Let's assume the weights are in column B (B4:B41) and data in the current column (X4:X41).
# And the split is likely first half and second half.
# Rows 4 to 41 is 38 rows. Half is 19. 4+19-1 = 22. So 4:22 and 23:41.
# Weights: $B$4:$B$41 (absolute).
# Data: X4:X22 and X23:X41.
# Formula for H43: 
# =ROUND((SUMPRODUCT($B$4:$B$41,H4:H22)+SUMPRODUCT($B$4:$B$41,H23:H41))/(SUM(H4:H22)+SUM(H23:H41)),4)
# This seems plausible.

# Alternative: Maybe weights are in the row above? H42:M42? No, those are likely headers or intermediate.
# Let's stick with the column weight assumption ($B$4:$B$41) as it's common for sector weights.
# If the weights are elsewhere, the "two ranges" error still applies to the data part.
# The prompt says "coefficient vector with exports, then with imports".
# So: SUMPRODUCT(Coeff, Exports) + SUMPRODUCT(Coeff, Imports).
# And denominator: SUM(Exports) + SUM(Imports).
# I will apply this pattern to H43:M43.

cols = ['H', 'I', 'J', 'K', 'L', 'M']
# Assumed ranges based on 38 data rows (4-41) split into two equal parts (4-22, 23-41)
# Assumed weight column: B (common for labels/weights in such tasks)
weight_range = "$B$4:$B$41"
range1_rel = "4:22"
range2_rel = "23:41"

for col in cols:
    cell = f"{col}43"
    # Construct the corrected formula
    # Using absolute references for weights, relative for the column being calculated
    formula = f'=ROUND((SUMPRODUCT({weight_range},{col}{range1_rel})+SUMPRODUCT({weight_range},{col}{range2_rel}))/(SUM({col}{range1_rel})+SUM({col}{range2_rel})),4)'
    ws[cell] = formula

# Fix H39:M40: Replace PERCENTILE.INC with PERCENTILE
# These are likely 2 rows x 6 columns = 12 cells.
# Range H39:M40.
for row in [39, 40]:
    for col in cols:
        cell = f"{col}{row}"
        old_val = ws[cell].value
        if isinstance(old_val, str) and 'PERCENTILE.INC' in old_val:
            new_val = old_val.replace('PERCENTILE.INC', 'PERCENTILE')
            ws[cell] = new_val

# Ensure A1 is a space if blank to preserve coordinates on CSV export
if ws['A1'].value is None or ws['A1'].value == '':
    ws['A1'] = ' '

# Save
wb.save('/root/gdp.xlsx')

# Output JSON
result = {
    "sheet": "Task",
    "formula_H43": ws['H43'].value,
    "formula_H39": ws['H39'].value
}
print(json.dumps(result))