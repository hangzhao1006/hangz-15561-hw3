# Data

The analysis uses the Northwind SQLite database, placed at:

```
data/northwind.db
```

The database file itself is not committed to the repository. To
reproduce the results, download the populated Northwind database
(~24 MB) from the public
[jpwhite3/northwind-SQLite3](https://github.com/jpwhite3/northwind-SQLite3)
project:

```bash
curl -sL -o data/northwind.db https://github.com/jpwhite3/northwind-SQLite3/raw/main/dist/northwind.db
```

Snapshot used for this homework: 16,282 orders and 609,283 order-detail
rows, with order dates from 2012-07 to 2023-10. All analysis scripts in
`analysis/` read from this path.
