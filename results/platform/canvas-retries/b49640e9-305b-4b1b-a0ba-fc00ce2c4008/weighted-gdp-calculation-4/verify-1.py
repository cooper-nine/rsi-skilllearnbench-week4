import json
import openpyxl

wb_path = "/root/gdp.xlsx"
wb = openpyxl.load_workbook(wb_path, data_only=False, keep_vba=True)

ws = wb["Task"]
cell_a1 = ws["A1"]
original_value = cell_a1.value
modified = False

if original_value is None or original_value == "":
    ws["A1"] = " "
    modified = True
    cell_a1 = ws["A1"]

wb.save(wb_path)
wb.close()

result = {
    "workbook_path": wb_path,
    "sheet_name": "Task",
    "cell_inspected": "A1",
    "original_value": str(original_value) if original_value is not None else None,
    "current_value": str(cell_a1.value),
    "was_modified": modified
}

print(json.dumps(result))