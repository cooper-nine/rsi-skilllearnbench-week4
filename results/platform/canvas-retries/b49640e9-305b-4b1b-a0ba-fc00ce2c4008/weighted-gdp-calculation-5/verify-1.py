import openpyxl
import json
import os

wb_path = "/root/gdp.xlsx"
wb = openpyxl.load_workbook(wb_path)

ws = wb["Task"]
cell_a1 = ws["A1"]
original_value = cell_a1.value
modified = False

if original_value is None or original_value == "":
    ws["A1"] = " "
    modified = True

wb.save(wb_path)

result = {
    "workbook_path": wb_path,
    "sheet_name": "Task",
    "cell_inspected": "A1",
    "original_value": str(original_value) if original_value is not None else None,
    "new_value": ws["A1"].value,
    "modified": modified
}

print(json.dumps(result))