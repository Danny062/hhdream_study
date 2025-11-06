from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_material_numbers_from_excel(path: str | Path, column_name: str) -> list[str]:
    """Reads a specific column from all sheets of an Excel file."""
    path = Path(path)

    if not path.exists():
        print(f"File not found: {path}")
        return []

    try:
        engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
        data = pd.read_excel(path, engine=engine, sheet_name=None)
    except Exception as e:
        print(f"Error reading Excel file {path}: {e}")
        return []

    material_numbers: list[str] = []
    for sheet_name, df in data.items():
        if column_name in df.columns:
            numbers = (
                df[column_name]
                .dropna()
                .astype(str)
                .map(str.strip)
                .tolist()
            )
            material_numbers.extend(filter(None, numbers))

    # Return unique values while preserving no order requirement
    return list({number for number in material_numbers})