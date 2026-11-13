# Data

The analysis uses the **course-provided Northwind dataset** (15.561),
distributed as a Google Sheets workbook and committed here as:

```
data/course/northwind_course.xlsx
```

Snapshot: 830 orders and 2,155 order-detail lines from 91 customers in
21 countries, order dates July 1996 – May 1998, 77 products.

The SQLite database the scripts read is **built from that workbook** and
is not committed. To (re)build it:

```bash
cd analysis
python build_db.py   # writes data/northwind.db
```

The build maps each worksheet to its canonical Northwind table name
(e.g. "Orders Details" → `Order Details`, "Product" → `Products`). All
analysis scripts in `analysis/` read from `data/northwind.db`.
