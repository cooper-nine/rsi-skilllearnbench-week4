import json
from openpyxl import load_workbook

wb_path = "/root/gdp.xlsx"
wb = load_workbook(wb_path)

ws = wb.active
if ws.title != "Task":
    for sheet_name in wb.sheetnames:
        if sheet_name == "Task":
            ws = wb[sheet_name]
            break

cell_a1 = ws['A1']
original_value = cell_a1.value
modified = False

if original_value is None or (isinstance(original_value, str) and original_value.strip() == ""):
    ws['A1'] = " "
    modified = True

wb.save(wb_path)
wb.close()

result = {
    "workbook_path": wb_path,
    "sheet_name": ws.title,
    "cell_a1_inspected": "A1",
    "original_value": original_value,
    "modified": modified,
    "current_value": ws['A1'].value if modified else original_value
}

print(json.dumps(result))
