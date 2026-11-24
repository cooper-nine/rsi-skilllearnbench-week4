"""Fill the existing Task sheet from the original Data ranges."""
from openpyxl import load_workbook


def main(instance):
    workbook = load_workbook("/root/gdp.xlsx")
    sheet = workbook["Task"]
    trade = instance == 5
    # Keep the Task sheet's row coordinates when exporting its used range.
    if sheet["A1"].value is None:
        sheet["A1"] = "GCC Trade Balance Coefficient" if trade else "GCC Net Exports as a Percentage of GDP"
    last_data = 33 if trade else 40
    groups = (12, 19) if trade else (12, 19, 26)
    first = 28 if trade else 35
    for column in ("HIJKLM" if trade else "HIJKL"):
        if sheet[f"{column}10"].value is None:
            source_column = column if trade else chr(ord(column) + 1)
            sheet[f"{column}10"] = workbook["Data"][f"{source_column}4"].value
        for start in groups:
            for row in range(start, start + 6):
                sheet[f"{column}{row}"] = (
                    f"=INDEX(Data!$H$21:$M${last_data},MATCH($D{row},Data!$B$21:$B${last_data},0),"
                    f"MATCH({column}$10,Data!$H$4:$M$4,0))"
                )
        for i in range(6):
            exports, imports = f"{column}{12+i}", f"{column}{19+i}"
            denominator = f"({exports}+{imports})" if trade else f"{column}{26+i}"
            sheet[f"{column}{first+i}"] = f"=ROUND(({exports}-{imports})/{denominator}*100,1)"
        values = f"{column}${first}:{column}${first+5}"
        for offset, function in enumerate(("MIN", "MAX", "MEDIAN", "AVERAGE", "PERCENTILE", "PERCENTILE")):
            extra = {4: ",0.25", 5: ",0.75"}.get(offset, "")
            sheet[f"{column}{first+7+offset}"] = f"=ROUND({function}({values}{extra}),1)"
        weight = (f"{column}$12:{column}$17+{column}$19:{column}$24"
                  if trade else f"{column}$26:{column}$31")
        total = (f"SUM({column}$12:{column}$17,{column}$19:{column}$24)"
                 if trade else f"SUM({weight})")
        sheet[f"{column}{first+15}"] = f"=ROUND(SUMPRODUCT({values},{weight})/{total},1)"
    workbook.save("/root/gdp.xlsx")


if __name__ == "__main__":
    import sys

    main(int(sys.argv[1]))
