import json
from openpyxl import load_workbook

# Load the workbook
wb = load_workbook('/root/gdp.xlsx')
task_sheet = wb['Task']
data_sheet = wb['Data']

# Define year columns in Task sheet (H to M)
task_year_cols = [8, 9, 10, 11, 12, 13]  # H, I, J, K, L, M
# Define year columns in Data sheet (H to M)
data_year_cols = [8, 9, 10, 11, 12, 13]  # H, I, J, K, L, M

# Step 1: Fill data in H12:M17 (Exports) and H19:M24 (Imports) using INDEX/MATCH
# For Exports (rows 12-17), series code is in column D, match against Data column B (series_code)
# Data rows for exports: 21-26 (Bahrain, Kuwait, Oman, Qatar, Saudi Arabia, UAE)
# But Task rows 12-17 are: UAE, Bahrain, Kuwait, Qatar, Oman, Saudi Arabia
# We need to match series code from Task D12:D17 to Data B21:B26

for row in range(12, 18):  # Rows 12 to 17
    series_code_cell = f'D{row}'
    for col_idx, data_col in enumerate(data_year_cols):
        task_col = task_year_cols[col_idx]
        cell_coord = f'{chr(64 + task_col)}{row}'
        # Formula: INDEX(Data!H:M, MATCH(series_code, Data!B:B, 0), year_column_index)
        # Data years are in H4:M4, data values start at row 21 for exports
        # We need to find the row in Data where series code matches
        # Then get the value from the corresponding year column
        # Using INDEX/MATCH with two conditions: series code and year header
        # Since year headers are in row 4 of Data sheet
        year_header_cell = f'{chr(64 + data_col)}4'
        # Match series code in Data column B
        # Match year header in Data row 4
        # Use INDEX to get the value
        formula = f'=INDEX(Data!H21:M26, MATCH({series_code_cell}, Data!B21:B26, 0), MATCH({year_header_cell}, Data!H4:M4, 0))'
        task_sheet[cell_coord] = formula

# For Imports (rows 19-24), series code is in column D, match against Data column B
# Data rows for imports: 28-33
for row in range(19, 25):  # Rows 19 to 24
    series_code_cell = f'D{row}'
    for col_idx, data_col in enumerate(data_year_cols):
        task_col = task_year_cols[col_idx]
        cell_coord = f'{chr(64 + task_col)}{row}'
        year_header_cell = f'{chr(64 + data_col)}4'
        formula = f'=INDEX(Data!H28:M33, MATCH({series_code_cell}, Data!B28:B33, 0), MATCH({year_header_cell}, Data!H4:M4, 0))'
        task_sheet[cell_coord] = formula

# Step 2: Calculate Trade Balance Coefficients in H28:M33
# Formula: (Exports - Imports) / (Exports + Imports) * 100
# Exports are in rows 12-17, Imports are in rows 19-24
# For each country row (28-33), corresponding export row is (row - 16) and import row is (row - 9)
# Row 28 -> Export row 12, Import row 19
# Row 29 -> Export row 13, Import row 20
# etc.

for row in range(28, 34):  # Rows 28 to 33
    export_row = row - 16
    import_row = row - 9
    for col_idx, task_col in enumerate(task_year_cols):
        cell_coord = f'{chr(64 + task_col)}{row}'
        export_cell = f'{chr(64 + task_col)}{export_row}'
        import_cell = f'{chr(64 + task_col)}{import_row}'
        formula = f'=ROUND(({export_cell}-{import_cell})/({export_cell}+{import_cell})*100, 1)'
        task_sheet[cell_coord] = formula

# Step 2 continued: Calculate statistics in rows 35-40
# min, max, median, simple mean, 25th percentile, 75th percentile
# Data range for each year: H28:H33, I28:I33, etc.

stats_rows = {
    35: 'MIN',
    36: 'MAX',
    37: 'MEDIAN',
    38: 'AVERAGE',
    39: 'QUARTILE',  # 25th percentile
    40: 'QUARTILE'   # 75th percentile
}

for row, stat_func in stats_rows.items():
    for col_idx, task_col in enumerate(task_year_cols):
        cell_coord = f'{chr(64 + task_col)}{row}'
        data_range = f'{chr(64 + task_col)}28:{chr(64 + task_col)}33'
        if stat_func == 'QUARTILE':
            quart = 1 if row == 39 else 3
            formula = f'=ROUND(QUARTILE({data_range}, {quart}), 1)'
        else:
            formula = f'=ROUND({stat_func}({data_range}), 1)'
        task_sheet[cell_coord] = formula

# Step 3: Calculate weighted mean in row 43
# Weighted mean = SUMPRODUCT(Trade Balance Coefficient, Total Trade Volume) / SUM(Total Trade Volume)
# Total Trade Volume = Exports + Imports
# Trade Balance Coefficients are in H28:M33
# Exports are in H12:M17, Imports are in H19:M24
# For each year column, we need to calculate:
# SUMPRODUCT(coefficients, volumes) / SUM(volumes)
# Where coefficients are H28:H33, volumes are (H12:H17 + H19:H24)

for col_idx, task_col in enumerate(task_year_cols):
    cell_coord = f'{chr(64 + task_col)}43'
    col_letter = chr(64 + task_col)
    
    # Coefficient range
    coeff_range = f'{col_letter}28:{col_letter}33'
    
    # Export range
    export_range = f'{col_letter}12:{col_letter}17'
    
    # Import range
    import_range = f'{col_letter}19:{col_letter}24'
    
    # Volume range (exports + imports) - we need to create this as an array
    # In Excel, we can use: (export_range + import_range)
    # SUMPRODUCT(coeff_range, export_range + import_range) / SUM(export_range + import_range)
    
    formula = f'=ROUND(SUMPRODUCT({coeff_range}, ({export_range}+{import_range})) / SUM({export_range}+{import_range}), 1)'
    task_sheet[cell_coord] = formula

# Save the workbook
wb.save('/root/gdp.xlsx')

# Output success message
print(json.dumps({"status": "success", "message": "Formulas filled successfully"}))
