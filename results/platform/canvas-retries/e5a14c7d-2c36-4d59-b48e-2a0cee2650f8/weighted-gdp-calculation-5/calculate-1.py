import json
from openpyxl import load_workbook

# Load the workbook
wb = load_workbook('/root/gdp.xlsx')
task_sheet = wb['Task']
data_sheet = wb['Data']

# Define ranges based on the task description and observed layout
# Data Sheet:
# Exports (BXGS_BP6): Rows 21-26, Series Code in Col B, Years in H4:M4, Data in H21:M26
# Imports (BMGS_BP6): Rows 28-33, Series Code in Col B, Years in H4:M4, Data in H28:M33
# GDP (NGDPD): Rows 35-40, Series Code in Col B, Years in H4:M4, Data in H35:M40

# Task Sheet:
# Step 1 Targets:
# Exports: H12:M17 (Rows 12-17 correspond to UAE, Bahrain, Kuwait, Qatar, Oman, Saudi Arabia)
#   Series Codes in D12:D17
# Imports: H19:M24 (Rows 19-24 correspond to same countries)
#   Series Codes in D19:D24
# Year headers in Task are in Row 9 (H9:M9)

# Step 2 Targets: Trade Balance Coefficient
# Rows 28-33, Cols H-M
# Formula: (Exports - Imports) / (Exports + Imports) * 100
# Exports for row r are in Task sheet row (r-16) -> e.g., Row 28 uses Row 12
# Imports for row r are in Task sheet row (r-10) -> e.g., Row 28 uses Row 19
# Wait, let's map carefully:
# Row 28 (UAE) -> Exports Row 12, Imports Row 19. Diff = 16.
# Row 29 (Bahrain) -> Exports Row 13, Imports Row 20. Diff = 16.
# So Exports Row = Current Row - 16. Imports Row = Current Row - 9.

# Step 3 Targets: Statistics (Rows 35-40) and Weighted Mean (Row 43)
# Statistics calculate over H28:M33 columns.
# Weighted Mean uses SUMPRODUCT of (Coefficient * GDP) / SUM(GDP).
# GDP data needs to be pulled into Task sheet or referenced directly? 
# The prompt says "fill formulas only" using original data. 
# Usually, for weighted mean, we need the GDP values for the specific year and country.
# We can use INDEX/MATCH to pull GDP dynamically into the formula or reference a helper range.
# However, the task says "fill formulas only" in the yellow ranges. 
# The yellow range for weighted mean is likely just E43? Or H43:M43?
# Looking at "task_target_blocks": {"start_row": 43, "end_row": 43, "type": "weighted_mean"}
# And labels: ["E43", "Trade Balance Coefficient, Percent, weighted mean"]
# This suggests the result might be a single value or per year? 
# "weighted mean for the GCC" usually implies one number per year if time series, or one overall.
# Given the layout H9:M9 are years, and previous steps have columns H-M, it's likely H43:M43.
# But the label is in E43. Let's assume H43:M43 are the target cells for the weighted mean per year.
# Actually, looking at the pattern, statistics rows 35-40 have labels in E, and values in H-M.
# So Row 43 should have values in H43:M43.

# Helper function to create INDEX/MATCH formula for Data lookup
# Data Sheet Structure:
# Col B: Series Code
# Col H-M: Data (Years in H4:M4)
# We need to match Series Code (Col B) and Year (Header Row 4)
# Formula for a cell in Task (e.g., H12):
# =INDEX(Data!$H$21:$M$33, MATCH($D12, Data!$B$21:$B$33, 0), MATCH(H$9, Data!$H$4:$M$4, 0))
# But we must restrict the row range to the correct block (Exports vs Imports).
# For Exports (Rows 12-17), source is Data!$H$21:$M$26.
# For Imports (Rows 19-24), source is Data!$H$28:$M$33.

cols = ['H', 'I', 'J', 'K', 'L', 'M']
col_indices = [8, 9, 10, 11, 12, 13] # 1-based

# Step 1: Populate Exports (Rows 12-17)
# Source: Data rows 21-26
for r in range(12, 18):
    for i, col in enumerate(cols):
        cell_coord = f"{col}{r}"
        # Match Series Code in D[r] against Data!B21:B26
        # Match Year in [col]9 against Data!H4:M4
        # Data range: H21:M26
        formula = f'=INDEX(Data!$H$21:$M$26, MATCH($D{r}, Data!$B$21:$B$26, 0), MATCH({col}$9, Data!$H$4:$M$4, 0))'
        task_sheet[cell_coord] = formula

# Step 1: Populate Imports (Rows 19-24)
# Source: Data rows 28-33
for r in range(19, 25):
    for i, col in enumerate(cols):
        cell_coord = f"{col}{r}"
        # Match Series Code in D[r] against Data!B28:B33
        # Match Year in [col]9 against Data!H4:M4
        # Data range: H28:M33
        formula = f'=INDEX(Data!$H$28:$M$33, MATCH($D{r}, Data!$B$28:$B$33, 0), MATCH({col}$9, Data!$H$4:$M$4, 0))'
        task_sheet[cell_coord] = formula

# Step 2: Calculate Trade Balance Coefficient (Rows 28-33)
# Formula: (Exp - Imp) / (Exp + Imp) * 100
# Exp is 16 rows above (28-16=12), Imp is 9 rows above (28-9=19)
for r in range(28, 34):
    exp_row = r - 16
    imp_row = r - 9
    for col in cols:
        cell_coord = f"{col}{r}"
        # Use absolute column for year reference if needed, but relative is fine if copied across
        # Ensure we reference the specific cells
        formula = f'=ROUND((( {col}{exp_row} - {col}{imp_row} ) / ( {col}{exp_row} + {col}{imp_row} )) * 100, 1)'
        task_sheet[cell_coord] = formula

# Step 2: Statistics (Rows 35-40)
# Range for calculation: H28:M33
# We need per-column stats (i.e., for each year column H, I, J, K, L, M)
# Row 35: MIN
# Row 36: MAX
# Row 37: MEDIAN
# Row 38: AVERAGE (Simple Mean)
# Row 39: 25th Percentile (QUARTILE.INC(..., 1) or PERCENTILE.INC(..., 0.25))
# Row 40: 75th Percentile (QUARTILE.INC(..., 3) or PERCENTILE.INC(..., 0.75))

stats_formulas = {
    35: 'MIN',
    36: 'MAX',
    37: 'MEDIAN',
    38: 'AVERAGE',
    39: 'PERCENTILE.INC',
    40: 'PERCENTILE.INC'
}

for r, func in stats_formulas.items():
    for col in cols:
        cell_coord = f"{col}{r}"
        if func == 'PERCENTILE.INC':
            # Determine k value
            k = 0.25 if r == 39 else 0.75
            formula = f'=ROUND({func}({col}$28:{col}$33, {k}), 1)'
        else:
            formula = f'=ROUND({func}({col}$28:{col}$33), 1)'
        task_sheet[cell_coord] = formula

# Step 3: Weighted Mean (Row 43)
# Formula: SUMPRODUCT(Coefficients, GDPs) / SUM(GDPs) * 100? 
# The coefficient is already a percent. The definition of weighted mean of a ratio:
# Sum(w_i * x_i) / Sum(w_i). Here x_i is the coefficient, w_i is the trade volume (Exp+Imp) or GDP?
# Prompt: "Trade Balance Coefficients as percent of total trade volume (exports + imports) weighted mean"
# This phrasing is slightly ambiguous. 
# Interpretation A: Weight the Coefficient by Total Trade Volume (Exp+Imp).
# Interpretation B: The coefficient IS (Exp-Imp)/(Exp+Imp). The "weighted mean" might refer to aggregating first then calculating ratio?
# No, it says "weighted mean FOR THE GCC ... using SUMPRODUCT".
# Standard weighted mean of coefficients: Sum(Coeff_i * Weight_i) / Sum(Weight_i).
# What is the weight? "percent of total trade volume" might describe the coefficient itself, not the weight.
# Or it means weight by Total Trade Volume?
# Let's re-read: "calculate the Trade Balance Coefficients as percent of total trade volume (exports + imports) weighted mean"
# This likely means: Calculate the weighted mean of the Trade Balance Coefficients, where the weights are the Total Trade Volumes (Exports + Imports).
# Why? Because larger economies/trade volumes should have more impact.
# However, often "weighted mean" in this context with GDP mentioned in Step 3 title ("weighted mean for the GCC") might imply GDP weights.
# But the text says "as percent of total trade volume ... weighted mean".
# Let's look at the data available. We have Exports and Imports in Task sheet (Rows 12-17, 19-24).
# We can calculate Total Trade Volume = Exp + Imp.
# So Weight = (Exp + Imp). Value = Coefficient.
# Formula for H43: SUMPRODUCT(H28:H33, (H12:H17 + H19:H24)) / SUM(H12:H17 + H19:H24)
# Wait, the coefficient is derived from Exp/Imp. If we weight by (Exp+Imp), the math simplifies:
# Sum( ((E-I)/(E+I)) * (E+I) ) / Sum(E+I) = Sum(E-I) / Sum(E+I).
# This is the aggregate trade balance coefficient for the whole bloc.
# This makes perfect sense economically.
# So the formula is: SUM(Exp - Imp) / SUM(Exp + Imp) * 100.
# Using SUMPRODUCT as requested:
# Numerator: SUMPRODUCT of 1 and (Exp-Imp)? Or just SUM(Exp)-SUM(Imp).
# The prompt explicitly asks to use SUMPRODUCT.
# Maybe they want: SUMPRODUCT(Coefficients, Weights) / SUM(Weights).
# Let's construct the ranges.
# Coefficients: H28:H33
# Weights (Total Trade): H12:H17 + H19:H24. Excel doesn't support array addition inside SUMPRODUCT directly without helper columns in older versions, but modern Excel does.
# Alternatively, since the result is mathematically equivalent to Sum(Net)/Sum(Total), we can do:
# =SUM(H12:H17 - H19:H24) / SUM(H12:H17 + H19:H24) * 100 -> This requires array formula entry in older Excel.
# To use SUMPRODUCT safely:
# SUMPRODUCT((H28:H33/100), (H12:H17+H19:H24)) / SUM(H12:H17+H19:H24) * 100?
# Actually, if we assume the "SUMPRODUCT" requirement is strict, we might need to compute the weights in a way SUMPRODUCT accepts.
# But SUMPRODUCT(H28:H33, H12:H17+H19:H24) works in modern Excel (365/2019+).
# Given the environment, let's try the direct aggregation which is robust:
# = (SUM(Exports) - SUM(Imports)) / (SUM(Exports) + SUM(Imports)) * 100
# But the prompt says "using the SUMPRODUCT formula".
# Okay, let's force SUMPRODUCT structure:
# Weighted Mean = SUMPRODUCT(Values, Weights) / SUM(Weights)
# Values = H28:H33 (already %)
# Weights = H12:H17 + H19:H24
# Formula: =SUMPRODUCT(H28:H33, H12:H17+H19:H24) / SUM(H12:H17+H19:H24)
# Note: H28:H33 is already multiplied by 100. So the result is correct.
# Let's verify the "GDP" part. The prompt mentions "weighted mean for the GCC" and Step 3 title.
# But the specific instruction says "as percent of total trade volume (exports + imports) weighted mean".
# This implies the weight is trade volume.
# If the weight was GDP, it would say "GDP-weighted".
# So I will use Trade Volume (Exp+Imp) as weights.

for col in cols:
    cell_coord = f"{col}43"
    exp_range = f"{col}12:{col}17"
    imp_range = f"{col}19:{col}24"
    coeff_range = f"{col}28:{col}33"
    
    # Constructing a formula that works with SUMPRODUCT for weights calculated on the fly
    # In Excel 365, SUMPRODUCT(coeff, exp+imp) works.
    # To be safe across versions, we can rely on the mathematical equivalence if SUMPRODUCT fails, 
    # but the instruction is explicit.
    # Let's try: =SUMPRODUCT({coeff_range}, {exp_range}+{imp_range}) / SUM({exp_range}+{imp_range})
    # If array ops in SUMPRODUCT are unsupported, we might need a different approach.
    # Alternative: The aggregate method SUM(Exp-Imp)/SUM(Exp+Imp) is the most robust "weighted mean" of ratios where weight is denominator.
    # And it can be written as SUMPRODUCT if we consider vectors.
    # Let's write the formula assuming modern Excel (which supports dynamic arrays in recalc scripts usually).
    # Formula: =ROUND(SUMPRODUCT({col}28:{col}33, ({col}12:{col}17+{col}19:{col}24)) / SUM({col}12:{col}17+{col}19:{col}24), 1)
    
    # However, if the engine is old, ({col}12:{col}17+{col}19:{col}24) inside SUMPRODUCT might fail.
    # A safer bet for "SUMPRODUCT" requirement with simple ranges is if we had a helper column, but we don't.
    # Let's assume the recalc engine supports modern Excel functions.
    # If not, the aggregate formula = (SUM(Exp)-SUM(Imp))/(SUM(Exp)+SUM(Imp))*100 is mathematically identical.
    # Does that use SUMPRODUCT? No.
    # How about: SUMPRODUCT( (Exp-Imp)/(Exp+Imp), (Exp+Imp) ) / SUM(Exp+Imp)
    # This expands to SUM(Exp-Imp) / SUM(Exp+Imp).
    # I will use the explicit SUMPRODUCT syntax as requested, hoping the engine supports array arithmetic within it.
    # Syntax: =SUMPRODUCT(values, weights) / SUM(weights)
    # Weights = Exp + Imp.
    
    formula = f'=ROUND(SUMPRODUCT({col}28:{col}33, ({col}12:{col}17+{col}19:{col}24)) / SUM({col}12:{col}17+{col}19:{col}24), 1)'
    
    # Fallback logic check: If the engine chokes on array add inside SUMPRODUCT, 
    # the only other interpretation is that weights are GDP.
    # But "percent of total trade volume" strongly points to trade volume weights.
    # I'll stick with the trade volume weight formula.
    
    task_sheet[cell_coord] = formula

# Save the workbook
wb.save('/root/gdp.xlsx')

# Output success JSON
print(json.dumps({"status": "success", "message": "Formulas filled successfully"}))
