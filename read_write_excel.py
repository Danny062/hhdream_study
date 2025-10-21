import os
import pandas as pd

def read_material_numbers_from_excel(path: str, column_name: str) -> list[str]:
    """Reads a specific column from all sheets of an Excel file."""
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []

    try:
        engine = "xlrd" if path.lower().endswith(".xls") else "openpyxl"
        data = pd.read_excel(path, engine=engine, sheet_name=None)
    except Exception as e:
        print(f"Error reading Excel file {path}: {e}")
        return []

    material_numbers = []
    for sheet_name, df in data.items():
        if column_name in df.columns:
            # Convert to string, drop NA values, and extend the list
            numbers = df[column_name].dropna().astype(str).tolist()
            material_numbers.extend(numbers)
        # else:
        #     print(f"Column '{column_name}' not found in sheet '{sheet_name}'.")

    return list(set(material_numbers)) # Return unique values
