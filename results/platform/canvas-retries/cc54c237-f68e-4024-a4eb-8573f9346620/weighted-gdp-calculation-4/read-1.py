import json
import openpyxl

def run():
    wb = openpyxl.load_workbook('/root/gdp.xlsx')
    
    result = {
        "Task": {
            "target_blocks": [],
            "data_indicator_blocks": [],
            "series_code_columns": [],
            "year_headers": []
        },
        "Data": {
            "target_blocks": [],
            "data_indicator_blocks": [],
            "series_code_columns": [],
            "year_headers": []
        }
    }

    # Analyze Task Sheet
    ws_task = wb['Task']
    
    # Identify Year Headers in Task (Row 9 and 10 based on context)
    task_years = []
    for col in range(1, 20):
        cell_9 = ws_task.cell(row=9, column=col)
        cell_10 = ws_task.cell(row=10, column=col)
        
        if cell_9.value is not None and isinstance(cell_9.value, (int, float)) or (isinstance(cell_9.value, str) and cell_9.value.isdigit()):
            val = int(float(cell_9.value)) if isinstance(cell_9.value, str) else int(cell_9.value)
            task_years.append({"coordinate": openpyxl.utils.get_column_letter(col) + "9", "value": str(val), "type": "numeric"})
            
        if cell_10.value is not None and isinstance(cell_10.value, (int, float)) or (isinstance(cell_10.value, str) and cell_10.value.isdigit()):
            # Avoid duplicates if row 9 and 10 are identical in logic, but map coordinates distinctly
            val = int(float(cell_10.value)) if isinstance(cell_10.value, str) else int(cell_10.value)
            # Check if this specific coordinate/year combo is already added to avoid redundancy if logic overlaps, 
            # but the prompt asks for coordinates on both sheets.
            task_years.append({"coordinate": openpyxl.utils.get_column_letter(col) + "10", "value": str(val), "type": "numeric"})

    result["Task"]["year_headers"] = task_years
    
    # Series Code Column in Task (Column D based on labels "Series code")
    result["Task"]["series_code_columns"] = ["D"]
    
    # Target Blocks in Task (Calculation areas: Step 2 and Step 3)
    # Step 2 starts around row 35, Step 3 around row 50
    # We identify blocks by looking for formula targets or specific labels like "Net Exports"
    task_targets = []
    # Scan rows 35-40 for Step 2
    for row in range(35, 41):
        if ws_task.cell(row=row, column=5).value: # Col E has label
            task_targets.append({
                "start": f"B{row}",
                "end": f"L{row}", # Assuming data goes to 2023 (Col L)
                "description": f"Step 2 Row {row}: {ws_task.cell(row=row, column=5).value}"
            })
    
    # Scan rows 42-47 for statistics
    for row in range(42, 48):
        if ws_task.cell(row=row, column=5).value:
            task_targets.append({
                "start": f"H{row}",
                "end": f"L{row}",
                "description": f"Statistic Row {row}: {ws_task.cell(row=row, column=5).value}"
            })
            
    # Scan row 50 for weighted mean
    if ws_task.cell(row=50, column=5).value:
        task_targets.append({
            "start": f"H50",
            "end": f"L50",
            "description": f"Weighted Mean Row 50: {ws_task.cell(row=50, column=5).value}"
        })
        
    result["Task"]["target_blocks"] = task_targets
    
    # Data Indicator Blocks in Task (Source data references: Rows 12-17, 19-24, 26-31)
    task_indicators = []
    ranges = [(12, 17), (19, 24), (26, 31)]
    for start_r, end_r in ranges:
        for r in range(start_r, end_r + 1):
            if ws_task.cell(row=r, column=4).value: # Series code exists
                task_indicators.append({
                    "coordinate": f"D{r}",
                    "series_code": ws_task.cell(row=r, column=4).value,
                    "country": ws_task.cell(row=r, column=3).value,
                    "indicator": ws_task.cell(row=r, column=5).value
                })
    result["Task"]["data_indicator_blocks"] = task_indicators

    # Analyze Data Sheet
    ws_data = wb['Data']
    
    # Identify Year Headers in Data (Row 4)
    data_years = []
    for col in range(1, 20):
        cell = ws_data.cell(row=4, column=col)
        if cell.value is not None and (isinstance(cell.value, (int, float)) or (isinstance(cell.value, str) and cell.value.isdigit())):
            val = int(float(cell.value)) if isinstance(cell.value, str) else int(cell.value)
            data_years.append({
                "coordinate": openpyxl.utils.get_column_letter(col) + "4", 
                "value": str(val), 
                "type": "numeric"
            })
    result["Data"]["year_headers"] = data_years
    
    # Series Code Column in Data (Column B based on header "Series_code")
    result["Data"]["series_code_columns"] = ["B"]
    
    # Data Indicator Blocks in Data (Rows with series codes)
    # Based on observed layout: Exports (21-26), Imports (28-33), GDP (35-40), Debt (42-47)
    data_indicators = []
    data_ranges = [(21, 26), (28, 33), (35, 40), (42, 47)]
    for start_r, end_r in data_ranges:
        for r in range(start_r, end_r + 1):
            series_code = ws_data.cell(row=r, column=2).value
            if series_code:
                data_indicators.append({
                    "coordinate": f"B{r}",
                    "series_code": series_code,
                    "country": ws_data.cell(row=r, column=3).value,
                    "indicator_name": ws_data.cell(row=r, column=5).value,
                    "unit": ws_data.cell(row=r, column=7).value
                })
    result["Data"]["data_indicator_blocks"] = data_indicators
    
    # Target Blocks in Data (The actual data values corresponding to years)
    # These are the blocks H6:M47 roughly
    data_targets = []
    # Group by logical sections
    sections = [
        {"name": "Morocco General", "rows": (6, 18)},
        {"name": "GCC Exports", "rows": (21, 26)},
        {"name": "GCC Imports", "rows": (28, 33)},
        {"name": "GCC GDP", "rows": (35, 40)},
        {"name": "GCC Debt", "rows": (42, 47)}
    ]
    
    for sec in sections:
        start_r, end_r = sec["rows"]
        for r in range(start_r, end_r + 1):
            if ws_data.cell(row=r, column=2).value: # If series code exists
                # Determine last column with data dynamically or assume M (2023)
                # Checking H to M
                data_targets.append({
                    "start": f"H{r}",
                    "end": f"M{r}",
                    "series_code": ws_data.cell(row=r, column=2).value,
                    "description": sec["name"]
                })
                
    result["Data"]["target_blocks"] = data_targets

    print(json.dumps(result))

if __name__ == "__main__":
    run()
