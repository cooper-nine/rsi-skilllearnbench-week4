"""Compute SEC filing answers using the human Skill's classification and ranking rules."""
import json
from pathlib import Path
import sys

import pandas as pd
from rapidfuzz import fuzz, process


def main(instance):
    sys.path[:0] = [str(path.parent) for path in Path("/root/.claude/skills").rglob("one_fund_analysis.py")]
    from one_fund_analysis import title_class_of_stocks

    def read(quarter, table):
        return pd.read_csv(f"/root/2025-q{quarter}/{table}.tsv", sep="\t", dtype=str)

    covers = {q: read(q, "COVERPAGE") for q in (2, 3)}
    holdings = {q: read(q, "INFOTABLE") for q in (2, 3)}
    for rows in holdings.values():
        rows["VALUE"] = pd.to_numeric(rows["VALUE"])

    def filing(q, name):
        available = covers[q].loc[(covers[q]["ISAMENDMENT"] != "Y")
                                 & covers[q]["ACCESSION_NUMBER"].isin(holdings[q]["ACCESSION_NUMBER"])]
        names = available["FILINGMANAGER_NAME"].dropna().unique().tolist()
        _, _, position = process.extractOne(name.casefold(), [value.casefold() for value in names],
                                            scorer=fuzz.WRatio)
        matched = names[position]
        accession = available.loc[available["FILINGMANAGER_NAME"] == matched, "ACCESSION_NUMBER"].iloc[0]
        return holdings[q].loc[holdings[q]["ACCESSION_NUMBER"] == accession]

    def stock_rows(rows):
        return rows.loc[rows["TITLEOFCLASS"].str.lower().isin(title_class_of_stocks)]

    def buys(name, limit):
        q2, q3 = (stock_rows(filing(q, name)).groupby("CUSIP")["VALUE"].sum() for q in (2, 3))
        increase = q3.subtract(q2, fill_value=0)
        return increase.loc[increase > 0].nlargest(limit).index.tolist()

    def managers(issuer, limit):
        choices = stock_rows(holdings[2]).drop_duplicates("CUSIP").dropna(subset=["NAMEOFISSUER"])
        _, _, position = process.extractOne(issuer.lower(), choices["NAMEOFISSUER"].str.lower().tolist(),
                                            scorer=fuzz.WRatio)
        cusip = choices.iloc[position]["CUSIP"]
        matched = holdings[3].loc[holdings[3]["CUSIP"] == cusip]
        ids = matched.groupby("ACCESSION_NUMBER")["VALUE"].sum().nlargest(limit).index
        names = covers[3].drop_duplicates("ACCESSION_NUMBER").set_index("ACCESSION_NUMBER")["FILINGMANAGER_NAME"]
        return names.loc[ids].tolist()

    if instance == 1:
        fund = filing(3, "renaissance technologies")
        result = dict(q1_answer=int(fund["VALUE"].sum()), q2_answer=len(stock_rows(fund)),
                      q3_answer=buys("berkshire hathaway", 5), q4_answer=managers("palantir", 3))
    else:
        fund = filing(3, "soros fund management")
        result = dict(q1_answer=int(fund["VALUE"].sum()), q2_answer=buys("pershing square capital management", 3),
                      q3_answer=managers("nvidia", 5))
    Path("/root/answers.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(int(sys.argv[1]))
