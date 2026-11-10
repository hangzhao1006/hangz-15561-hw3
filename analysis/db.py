"""Shared helpers for connecting to the Northwind SQLite database."""

import pathlib
import sqlite3

import pandas as pd

DATA_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "northwind.db"


def connect(db_path=DATA_PATH):
    """Open a read-only connection to the Northwind database.

    Args:
        db_path (pathlib.Path): Location of the SQLite file; defaults
            to ``data/northwind.db`` at the repository root.

    Returns:
        sqlite3.Connection: Read-only connection to the database.

    Raises:
        FileNotFoundError: If the database file does not exist.
    """
    if not pathlib.Path(db_path).exists():
        raise FileNotFoundError(
            f"Northwind database not found at {db_path}. "
            "See data/README.md for setup instructions."
        )
    return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


def query(sql, params=None, db_path=DATA_PATH):
    """Run a SQL query against the Northwind database.

    Args:
        sql (str): SQL statement to execute.
        params (dict | tuple | None): Bound parameters for the query.
        db_path (pathlib.Path): Location of the SQLite file; defaults
            to ``data/northwind.db`` at the repository root.

    Returns:
        pandas.DataFrame: Query results, one row per record.
    """
    with connect(db_path) as conn:
        return pd.read_sql_query(sql, conn, params=params)
