import json
from openpyxl import load_workbook

# Load the workbook
wb = load_workbook('/root/gdp.xlsx')
task_sheet = wb['Task']
data_sheet = wb['Data']

# Define ranges based on the observed layout and task description
# Data Sheet:
# Exports: Rows 21-26 (Series codes in B, Country in C, Data H-M)
# Imports: Rows 28-33
# GDP: Rows 35-40
# Years in Data sheet: H4=2018, I4=2019, J4=2020, K4=2021, L4=2022, M4=2023

# Task Sheet:
# Target Years: H9=2019, I9=2020, J9=2021, K9=2022, L9=2023
# We need to map Task Year columns (H-L) to Data Year columns (I-M)
# Task Col H (2019) -> Data Col I (2019)
# Task Col I (2020) -> Data Col J (2020)
# Task Col J (2021) -> Data Col K (2021)
# Task Col K (2022) -> Data Col L (2022)
# Task Col L (2023) -> Data Col M (2023)

# Helper to get column letter for offset
def get_col_letter(offset):
    # H is 8. Offset 0 -> H, 1 -> I, etc.
    return chr(ord('H') + offset)

data_col_map = {
    'H': 'I', # 2019
    'I': 'J', # 2020
    'J': 'K', # 2021
    'K': 'L', # 2022
    'L': 'M'  # 2023
}

# Step 1: Fill Exports (Rows 12-17), Imports (Rows 19-24), GDP (Rows 26-31)
# Using INDEX & MATCH with two conditions: Series Code (Col D) and Year (Row 9)
# Data Sheet Structure: Series Code in Col B, Years in Row 4 (H4:M4)
# We need to match the Series Code in Task Col D with Data Col B
# And match the Year in Task Row 9 with Data Row 4

# Formula pattern for Task cell (e.g., H12):
# =INDEX(Data!$H$21:$M$26, MATCH($D12, Data!$B$21:$B$26, 0), MATCH(H$9, Data!$H$4:$M$4, 0))
# Note: The data range in INDEX must correspond to the block being looked up.

# Exports Block (Task Rows 12-17, Data Rows 21-26)
for row in range(12, 18):
    series_cell = f'D{row}'
    for col_offset in range(5): # H to L (0 to 4)
        task_col = get_col_letter(col_offset)
        data_col = data_col_map[task_col]
        # Data range for exports is H21:M26. 
        # MATCH for year looks at H4:M4.
        formula = f'=INDEX(Data!$H$21:$M$26, MATCH(${series_cell}, Data!$B$21:$B$26, 0), MATCH({task_col}$9, Data!$H$4:$M$4, 0))'
        task_sheet[f'{task_col}{row}'] = formula

# Imports Block (Task Rows 19-24, Data Rows 28-33)
for row in range(19, 25):
    series_cell = f'D{row}'
    for col_offset in range(5):
        task_col = get_col_letter(col_offset)
        formula = f'=INDEX(Data!$H$28:$M$33, MATCH(${series_cell}, Data!$B$28:$B$33, 0), MATCH({task_col}$9, Data!$H$4:$M$4, 0))'
        task_sheet[f'{task_col}{row}'] = formula

# GDP Block (Task Rows 26-31, Data Rows 35-40)
for row in range(26, 32):
    series_cell = f'D{row}'
    for col_offset in range(5):
        task_col = get_col_letter(col_offset)
        formula = f'=INDEX(Data!$H$35:$M$40, MATCH(${series_cell}, Data!$B$35:$B$40, 0), MATCH({task_col}$9, Data!$H$4:$M$4, 0))'
        task_sheet[f'{task_col}{row}'] = formula

# Step 2: Calculate Net Exports % of GDP (Rows 35-40)
# Formula: (Exports - Imports) / GDP * 100
# Exports are in rows 12-17, Imports in 19-24, GDP in 26-31.
# Mapping: 
# Row 35 (UAE) uses Exports Row 12, Imports Row 19, GDP Row 26
# Row 36 (Bahrain) uses Exports Row 13, Imports Row 20, GDP Row 27
# ...
# Offset mapping: Task Row 35 -> Exp 12 (diff -23), Imp 19 (diff -16), GDP 26 (diff -9)

for row in range(35, 41):
    exp_row = row - 23
    imp_row = row - 16
    gdp_row = row - 9
    for col_offset in range(5):
        task_col = get_col_letter(col_offset)
        # Round to 1 decimal place as requested
        formula = f'=ROUND((({task_col}{exp_row}-{task_col}{imp_row})/{task_col}{gdp_row})*100, 1)'
        task_sheet[f'{task_col}{row}'] = formula

# Step 2 continued: Statistics (Rows 42-47)
# Columns H-L, calculating across rows 35-40 for each column
stats_config = [
    (42, 'MIN'),
    (43, 'MAX'),
    (44, 'MEDIAN'),
    (45, 'AVERAGE'),
    (46, 'QUARTILE.INC', 1), # 25th percentile
    (47, 'QUARTILE.INC', 3)  # 75th percentile
]

for stat_row, func_name, *args in stats_config:
    for col_offset in range(5):
        task_col = get_col_letter(col_offset)
        range_str = f'{task_col}35:{task_col}40'
        if func_name == 'QUARTILE.INC':
            formula = f'=ROUND({func_name}({range_str}, {args[0]}), 1)'
        else:
            formula = f'=ROUND({func_name}({range_str}), 1)'
        task_sheet[f'{task_col}{stat_row}'] = formula

# Step 3: Weighted Mean (Row 50)
# Weighted Mean = SUMPRODUCT(Net Exports Value, GDP Value) / SUM(GDP Value)
# But we need the result as a percentage.
# Net Exports Value = (Exp - Imp). GDP Value = GDP.
# Weighted Mean % = SUMPRODUCT((Exp-Imp), GDP) / SUM(GDP) * 100
# However, the cells H35:L40 already contain the percentage. 
# The standard weighted mean of percentages uses the weights (GDP) and the values (Net Exp %).
# Formula: SUMPRODUCT(Weights, Values) / SUM(Weights)
# Weights are GDP (Rows 26-31). Values are Net Exp % (Rows 35-40).
# Since Net Exp % = (Exp-Imp)/GDP, then Weight * Value = (Exp-Imp).
# So SUMPRODUCT(GDP, NetExp%) = Sum(Exp-Imp).
# Then divide by Sum(GDP) and multiply by 100? 
# Wait, H35:L40 are already multiplied by 100 and rounded. 
# To be precise with weights, we should use the raw numbers if possible, but we only have the rounded percentages in the sheet now?
# No, the formula in H35 references the raw data. 
# Let's construct the weighted mean formula using the raw components to avoid rounding errors accumulation, 
# or use the calculated percentage cells if that's what "using the SUMPRODUCT formula" implies directly on the result rows.
# Given the instruction "Calculate the net exports as percent of GDP weighted mean... by using the SUMPRODUCT formula",
# and the previous step rounded the individual percentages, using the rounded values might be slightly off but follows the flow.
# However, a more robust approach for "weighted mean of net exports as a percentage" is:
# Total Net Exports / Total GDP * 100.
# Total Net Exports = SUM(Exp - Imp) = SUMPRODUCT(1, Exp-Imp)
# Total GDP = SUM(GDP)
# Let's try to interpret "SUMPRODUCT" literally.
# SUMPRODUCT(Weights, Values) / SUM(Weights).
# Weights = GDP (Row 26-31). Values = Net Exp % (Row 35-40).
# If we use the cells H35:H40 which are already *100, then the result is the weighted average of those percentages.
# Formula: =SUMPRODUCT(GDP_Range, NetExpPct_Range) / SUM(GDP_Range)
# This will yield the weighted average of the percentages displayed.

for col_offset in range(5):
    task_col = get_col_letter(col_offset)
    gdp_range = f'{task_col}26:{task_col}31'
    net_exp_range = f'{task_col}35:{task_col}40'
    # The values in net_exp_range are already percentages (e.g., 12.3). 
    # So the weighted average will be in the same scale.
    formula = f'=ROUND(SUMPRODUCT({gdp_range}, {net_exp_range}) / SUM({gdp_range}), 1)'
    task_sheet[f'{task_col}50'] = formula

# Save the workbook
wb.save('/root/gdp.xlsx')

# Output success
print(json.dumps({"status": "success", "message": "Formulas filled successfully"}))
