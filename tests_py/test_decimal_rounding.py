"""Pin how fct_summary rounds mw and price to 4 decimals, on both engines.

A direct DOUBLE -> DECIMAL(18, 4) breaks ties differently on the two engines: Spark rounds
the shortest decimal form of the double, T-SQL its exact binary value, so every AEMO price
ending in 5 at the 5th decimal split them by 0.0001 (~500k rows in production, three days
past parity's tolerance). Going through DECIMAL(18, 6) holds the source value exactly, and
DECIMAL -> DECIMAL rounds half away from zero on both. Verified on Fabric Warehouse:
CAST(CAST(CAST('0.19005' AS FLOAT) AS DECIMAL(18,6)) AS DECIMAL(18,4)) is 0.1901, Spark's.

Run: python -m pytest tests_py/ -q
"""
from __future__ import annotations

import pytest

from _layout import ENGINES, REPO


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("column", ["mw", "price"])
def test_fct_summary_rounds_through_six_decimals(engine, column):
    sql = (REPO / "models" / "aemo" / engine / "marts" / "fct_summary.sql").read_text(encoding="utf-8")
    assert f"CAST(CAST({column} AS DECIMAL(18, 6)) AS DECIMAL(18, 4)) AS {column}" in sql
    assert f"CAST({column} AS DECIMAL(18, 4)) AS {column}" not in sql
