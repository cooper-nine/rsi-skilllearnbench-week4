import json
import openpyxl

def analyze_workbook():
    file_path = "/root/gdp.xlsx"
    wb = openpyxl.load_workbook(file_path, data_only=True)
    
    result = {
        "sheets": []
    }

    for sheet_name in ["Task", "Data"]:
        ws = wb[sheet_name]
        sheet_info = {
            "name": sheet_name,
            "task_target_blocks": [],
            "data_indicator_blocks": [],
            "series_code_columns": [],
            "year_headers": []
        }

        # Scan for year headers (numeric values typically in row 4 or 9, columns H onwards)
        # And identify blocks based on context
        
        max_row = ws.max_row
        max_col = ws.max_column
        
        # Identify Year Headers
        # Based on previous checkpoint and standard layout:
        # Task: Row 9 and Row 34 usually contain years
        # Data: Row 4 usually contains years
        
        potential_year_rows = [4, 9, 34]
        
        for r in range(1, max_row + 1):
            for c in range(1, max_col + 1):
                cell = ws.cell(row=r, column=c)
                val = cell.value
                
                # Detect Year Headers
                if isinstance(val, int) and 2000 <= val <= 2030:
                    coord = cell.coordinate
                    # Avoid duplicates if scanning multiple potential rows blindly, 
                    # but we want to capture all instances found in the sheet
                    sheet_info["year_headers"].append({
                        "coordinate": coord,
                        "value": val,
                        "row": r,
                        "col": c
                    })
                
                # Detect Series Code Columns
                # In 'Data', Column B is typically Series Code (e.g., "686NGDP.A")
                # In 'Task', Column D is typically Series Code
                if sheet_name == "Data" and c == 2 and r > 5: # Col B
                    if isinstance(val, str) and "." in val:
                         sheet_info["series_code_columns"].append({"coordinate": coord, "value": val})
                elif sheet_name == "Task" and c == 4 and r > 10: # Col D
                    if isinstance(val, str) and "." in val:
                        sheet_info["series_code_columns"].append({"coordinate": coord, "value": val})

        # Identify Blocks (Groupings of data)
        # Task Sheet:
        # Block 1: Rows 12-17 (Exports)
        # Block 2: Rows 19-24 (Imports)
        # Block 3: Rows 26-31 (GDP)
        # Block 4: Rows 35-40 (Calculation Targets)
        # Block 5: Rows 42-47 (Stats)
        # Block 6: Row 50 (Weighted Mean)
        
        if sheet_name == "Task":
            # Define target blocks based on known structure from prompt description
            blocks = [
                {"type": "Source_Exports", "start_row": 12, "end_row": 17},
                {"type": "Source_Imports", "start_row": 19, "end_row": 24},
                {"type": "Source_GDP", "start_row": 26, "end_row": 31},
                {"type": "Target_Calculation", "start_row": 35, "end_row": 40},
                {"type": "Target_Stats", "start_row": 42, "end_row": 47},
                {"type": "Target_Weighted", "start_row": 50, "end_row": 50}
            ]
            
            for block in blocks:
                # Get representative label from Column E or C
                label_cell = ws.cell(row=block["start_row"], column=5) # Col E
                label = label_cell.value if label_cell.value else "Unknown"
                
                sheet_info["task_target_blocks"].append({
                    "type": block["type"],
                    "row_range": [block["start_row"], block["end_row"]],
                    "label": label,
                    "coordinates": {
                        "country": ws.cell(row=block["start_row"], column=3).coordinate,
                        "series": ws.cell(row=block["start_row"], column=4).coordinate,
                        "data_start": ws.cell(row=block["start_row"], column=8).coordinate # Col H
                    }
                })

        # Data Sheet:
        # Blocks are contiguous rows of data starting from row 6 or 21
        # Exports: 21-26
        # Imports: 28-33
        # GDP: 35-40
        
        if sheet_name == "Data":
            data_blocks = [
                {"type": "Source_Exports", "start_row": 21, "end_row": 26},
                {"type": "Source_Imports", "start_row": 28, "end_row": 33},
                {"type": "Source_GDP", "start_row": 35, "end_row": 40}
            ]
            
            for block in data_blocks:
                label_cell = ws.cell(row=block["start_row"], column=5) # Col E
                label = label_cell.value if label_cell.value else "Unknown"
                
                sheet_info["data_indicator_blocks"].append({
                    "type": block["type"],
                    "row_range": [block["start_row"], block["end_row"]],
                    "label": label,
                    "coordinates": {
                        "series_code": ws.cell(row=block["start_row"], column=2).coordinate, # Col B
                        "country": ws.cell(row=block["start_row"], column=3).coordinate,
                        "data_start": ws.cell(row=block["start_row"], column=8).coordinate # Col H
                    }
                })

        result["sheets"].append(sheet_info)

    print(json.dumps(result))

if __name__ == "__main__":
    analyze_workbook()
