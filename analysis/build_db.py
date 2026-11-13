"""Build data/northwind.db from the course-provided Excel workbook."""

import pathlib
import sqlite3

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
XLSX_PATH = ROOT / "data" / "course" / "northwind_course.xlsx"
DB_PATH = ROOT / "data" / "northwind.db"

# Sheet name in the course workbook -> canonical Northwind table name.
SHEET_TO_TABLE = {
    "Categories": "Categories",
    "Customers": "Customers",
    "Employees": "Employees",
    "Orders Details": "Order Details",
    "Orders": "Orders",
    "Shippers": "Shippers",
    "Product": "Products",
    "Suppliers": "Suppliers",
}


def build(xlsx_path=XLSX_PATH, db_path=DB_PATH):
    """Convert the course workbook into a SQLite database.

    Args:
        xlsx_path (pathlib.Path): The course Excel file; one sheet per
            Northwind table.
        db_path (pathlib.Path): Destination SQLite file; overwritten if
            present.

    Returns:
        None. Writes ``db_path`` and prints each table's row count.
    """
    sheets = pd.read_excel(xlsx_path, sheet_name=None)
    db_path.unlink(missing_ok=True)
    with sqlite3.connect(db_path) as conn:
        for sheet_name, table in SHEET_TO_TABLE.items():
            df = sheets[sheet_name]
            # Drop unnamed spill-over columns from the spreadsheet.
            df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
            df.to_sql(table, conn, index=False, if_exists="replace")
            print(f"{table}: {len(df)} rows")


if __name__ == "__main__":
    build()
