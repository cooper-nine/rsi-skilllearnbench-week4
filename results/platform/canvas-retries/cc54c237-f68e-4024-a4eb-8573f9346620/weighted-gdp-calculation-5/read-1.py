import openpyxl
import json

def get_coordinate(row, col):
    return openpyxl.utils.get_column_letter(col) + str(row)

def analyze_workbook():
    wb = openpyxl.load_workbook('/root/gdp.xlsx', data_only=False)
    result = {
        "sheets": {},
        "year_headers_by_sheet": {}
    }

    for sheet_name in ["Task", "Data"]:
        ws = wb[sheet_name]
        sheet_data = {
            "task_target_blocks": [],
            "data_indicator_blocks": [],
            "series_code_columns": []
        }
        
        year_headers = []
        
        # Scan for year headers (numeric years typically 2018-2023+)
        # We look for cells containing integer years in the header regions
        for row in range(1, 50):
            for col in range(1, 20):
                cell = ws.cell(row=row, column=col)
                val = cell.value
                if isinstance(val, int) and 2010 <= val <= 2030:
                    coord = get_coordinate(row, col)
                    # Avoid duplicates if same year appears multiple times in logic, 
                    # but here we map specific coordinates found.
                    year_headers.append({
                        "coordinate": coord,
                        "value": val,
                        "row": row,
                        "column": col
                    })
        
        result["year_headers_by_sheet"][sheet_name] = year_headers

        # Identify blocks based on content patterns
        if sheet_name == "Task":
            # Step 1: Exports/Imports population block (Rows 12-24)
            # Step 2: Calculation block (Rows 28-33)
            # Step 3: Aggregation block (Rows 35-43)
            
            # Detect Series Code Column (Column D usually)
            series_col = None
            for r in range(10, 45):
                c_val = ws.cell(row=r, column=4).value # Col D
                if c_val and isinstance(c_val, str) and '.' in c_val and len(c_val) > 5:
                    series_col = 4
                    break
            
            if series_col:
                sheet_data["series_code_columns"].append(series_col)

            # Task Target Blocks: Areas where formulas or specific labels indicate calculation targets
            # Block 1: Rows 12-24 (Data entry references)
            sheet_data["task_target_blocks"].append({"start_row": 12, "end_row": 24, "type": "data_population"})
            # Block 2: Rows 28-33 (Trade Balance Coefficient)
            sheet_data["task_target_blocks"].append({"start_row": 28, "end_row": 33, "type": "calculation"})
            # Block 3: Rows 35-40 (Stats: min, max, median, mean, percentiles)
            sheet_data["task_target_blocks"].append({"start_row": 35, "end_row": 40, "type": "statistics"})
            # Block 4: Row 43 (Weighted mean)
            sheet_data["task_target_blocks"].append({"start_row": 43, "end_row": 43, "type": "weighted_mean"})

        elif sheet_name == "Data":
            # Data Indicator Blocks: Rows with actual data
            # Headers are at Row 4. Data starts Row 6.
            # Series Code is Column B
            
            sheet_data["series_code_columns"].append(2) # Column B
            
            # Identify contiguous blocks of data
            # Exports: 21-26
            # Imports: 28-33
            # GDP: 35-40
            # Debt: 42-47
            
            blocks = [
                {"start_row": 6, "end_row": 18, "type": "morocco_general"},
                {"start_row": 21, "end_row": 26, "type": "exports_bop"},
                {"start_row": 28, "end_row": 33, "type": "imports_bop"},
                {"start_row": 35, "end_row": 40, "type": "gdp_usd"},
                {"start_row": 42, "end_row": 47, "type": "debt_gdp"}
            ]
            
            # Verify blocks exist by checking if Series Code (Col B) is present
            valid_blocks = []
            for b in blocks:
                check_cell = ws.cell(row=b["start_row"], column=2).value
                if check_cell:
                    valid_blocks.append(b)
            
            sheet_data["data_indicator_blocks"] = valid_blocks

        result["sheets"][sheet_name] = sheet_data

    print(json.dumps(result))

if __name__ == "__main__":
    analyze_workbook()