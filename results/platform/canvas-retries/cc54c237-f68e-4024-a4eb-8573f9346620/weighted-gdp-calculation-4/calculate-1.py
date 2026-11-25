import json
from openpyxl import load_workbook

# Load the workbook
wb = load_workbook('/root/gdp.xlsx')
task_sheet = wb['Task']
data_sheet = wb['Data']

# Define the mapping for Task rows to Data series codes and countries
# Exports: Task 12-17 -> Data 26, 21, 22, 23, 24, 25 (based on series code match)
# Imports: Task 19-24 -> Data 33, 28, 29, 30, 31, 32
# GDP: Task 26-31 -> Data 40, 35, 36, 37, 38, 39

# Helper to get column letter from index (1-based)
def get_col_letter(n):
    letters = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters

# Year columns in Task: H=8, I=9, J=10, K=11, L=12
# Year columns in Data: H=8 (2018), I=9 (2019), J=10 (2020), K=11 (2021), L=12 (2022), M=13 (2023)
# Task years start at 2019 in col H. Data 2019 is in col I.
# So Task Col H (2019) -> Data Col I
# Task Col I (2020) -> Data Col J
# Offset: Data_Col_Index = Task_Col_Index + 1

task_year_cols = [8, 9, 10, 11, 12] # H, I, J, K, L
data_year_cols = [c + 1 for c in task_year_cols] # I, J, K, L, M

# Step 1: Fill H12:L17, H19:L24, H26:L31 using INDEX/MATCH
# We will construct formulas that look up the series code in Data!B:B and return the value from the corresponding year column.

# Mapping for Exports (Task Rows 12-17)
# Task D12=466BXGS_BP6.A -> Data B26
# Task D13=419BXGS_BP6.A -> Data B21
# Task D14=443BXGS_BP6.A -> Data B22
# Task D15=453BXGS_BP6.A -> Data B23
# Task D16=449BXGS_BP6.A -> Data B24
# Task D17=456BXGS_BP6.A -> Data B25
exports_map = {
    12: 26, 13: 21, 14: 22, 15: 23, 16: 24, 17: 25
}

# Mapping for Imports (Task Rows 19-24)
# Task D19=466BMGS_BP6.A -> Data B33
# Task D20=419BMGS_BP6.A -> Data B28
# Task D21=443BMGS_BP6.A -> Data B29
# Task D22=453BMGS_BP6.A -> Data B30
# Task D23=449BMGS_BP6.A -> Data B31
# Task D24=456BMGS_BP6.A -> Data B32
imports_map = {
    19: 33, 20: 28, 21: 29, 22: 30, 23: 31, 24: 32
}

# Mapping for GDP (Task Rows 26-31)
# Task D26=466NGDPD.A -> Data B40
# Task D27=419NGDPD.A -> Data B35
# Task D28=443NGDPD.A -> Data B36
# Task D29=453NGDPD.A -> Data B37
# Task D30=449NGDPD.A -> Data B38
# Task D31=456NGDPD.A -> Data B39
gdp_map = {
    26: 40, 27: 35, 28: 36, 29: 37, 30: 38, 31: 39
}

def write_lookup_formulas(sheet, row_map, start_col_idx, data_col_indices):
    for task_row, data_row in row_map.items():
        for i, t_col in enumerate(start_col_idx):
            d_col = data_col_indices[i]
            # Formula: =INDEX(Data!$H$4:$M$40, MATCH($D{task_row}, Data!$B$21:$B$40, 0) + offset_row, MATCH({year_val}, Data!$H$4:$M$4, 0))
            # Simpler: Use INDEX with MATCH on Series Code and Column Index for Year
            # Since we know the exact row in Data for each Task row via our map, we can just reference that row directly?
            # But instruction says "use two conditions: series code and year".
            # So we must use MATCH for series code.
            # Data Series Codes are in B21:B40.
            # Data Years are in H4:M4.
            
            # Construct formula:
            # =INDEX(Data!$H$21:$M$40, MATCH($D{row}, Data!$B$21:$B$40, 0), MATCH(H$10, Data!$H$4:$M$4, 0))
            # Note: Task year headers are in row 10 (H10:L10). Data year headers are in row 4 (H4:M4).
            # The range for values in Data is H21:M40.
            
            col_letter = get_col_letter(t_col)
            formula = f'=INDEX(Data!$H$21:$M$40, MATCH($D{task_row}, Data!$B$21:$B$40, 0), MATCH({col_letter}$10, Data!$H$4:$M$4, 0))'
            sheet[f'{col_letter}{task_row}'] = formula

# Apply Step 1
write_lookup_formulas(task_sheet, exports_map, task_year_cols, data_year_cols)
write_lookup_formulas(task_sheet, imports_map, task_year_cols, data_year_cols)
write_lookup_formulas(task_sheet, gdp_map, task_year_cols, data_year_cols)

# Step 2: Calculate Net Exports % of GDP in H35:L40
# Net Exports = Exports - Imports
# Rows 12-17 are Exports, Rows 19-24 are Imports, Rows 26-31 are GDP.
# Target Rows 35-40 correspond to countries in same order as 12-17.
# Row 35 (UAE) = (Row 12 - Row 19) / Row 26 * 100
# Row 36 (Bahrain) = (Row 13 - Row 20) / Row 27 * 100
# ...
# Formula: =(H12-H19)/H26*100
# Round to 1 decimal: ROUND(..., 1)

country_rows = [35, 36, 37, 38, 39, 40]
export_rows = [12, 13, 14, 15, 16, 17]
import_rows = [19, 20, 21, 22, 23, 24]
gdp_rows = [26, 27, 28, 29, 30, 31]

for i, tr in enumerate(country_rows):
    er = export_rows[i]
    ir = import_rows[i]
    gr = gdp_rows[i]
    for t_col in task_year_cols:
        col_l = get_col_letter(t_col)
        # Formula: =ROUND((H12-H19)/H26*100, 1)
        formula = f'=ROUND(({col_l}{er}-{col_l}{ir})/{col_l}{gr}*100, 1)'
        task_sheet[f'{col_l}{tr}'] = formula

# Step 2 Stats: Rows 42-47, Cols H-L
# Min, Max, Median, Mean, 25th %, 75th %
# Data range for each year: H35:H40, I35:I40, etc.
stats_rows = {
    42: 'MIN',
    43: 'MAX',
    44: 'MEDIAN',
    45: 'AVERAGE',
    46: 'QUARTILE', # 25th
    47: 'QUARTILE'  # 75th
}

for sr, func in stats_rows.items():
    for t_col in task_year_cols:
        col_l = get_col_letter(t_col)
        range_ref = f'{col_l}35:{col_l}40'
        if func == 'QUARTILE':
            if sr == 46:
                formula = f'=ROUND(QUARTILE({range_ref}, 1), 1)'
            else:
                formula = f'=ROUND(QUARTILE({range_ref}, 3), 1)'
        else:
            formula = f'=ROUND({func}({range_ref}), 1)'
        task_sheet[f'{col_l}{sr}'] = formula

# Step 3: Weighted Mean in Row 50
# Weighted Mean = SUMPRODUCT(NetExports, GDP) / SUM(GDP)
# But Net Exports in rows 35-40 are already percentages.
# The problem asks for "net exports as percent of GDP weighted mean".
# Usually this means: Sum(NetExports_abs) / Sum(GDP) * 100.
# NetExports_abs = Exports - Imports (values from step 1).
# So Weighted Mean = SUMPRODUCT((Exp-Imp), GDP) / SUM(GDP) * 100?
# Or since we have % in 35-40 and GDP in 26-31:
# Weighted Avg % = SUMPRODUCT(%_values, GDP_values) / SUM(GDP_values)
# Let's use the percentage values (35-40) and GDP values (26-31).
# Formula for H50: =SUMPRODUCT(H35:H40, H26:H31) / SUM(H26:H31)
# Round to 1 decimal.

for t_col in task_year_cols:
    col_l = get_col_letter(t_col)
    formula = f'=ROUND(SUMPRODUCT({col_l}35:{col_l}40, {col_l}26:{col_l}31) / SUM({col_l}26:{col_l}31), 1)'
    task_sheet[f'{col_l}50'] = formula

# Save the workbook
wb.save('/root/gdp.xlsx')

# Output result
print(json.dumps({"status": "success", "message": "Formulas filled successfully"}))
