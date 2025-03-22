import json
import pandas as pd
from shared import get_full_epd

def get_epd_by_id(uuid: str):
    """Fetches the data of a specific EPD given its UUID and returns it as JSON (no file saving)."""
    data = get_full_epd(uuid)  # Fetch EPD data

    return data  # ✅ Only return JSON, do NOT save it here


def convert_json_to_excel(json_file):
    """Converts a saved JSON file to an Excel file."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert JSON to DataFrame
    df = pd.json_normalize(data)  # Flattens nested JSON

    # Save to Excel
    excel_file = json_file.replace(".json", ".xlsx")
    df.to_excel(excel_file, index=False, engine="openpyxl")

    print(f"EPD data has been saved to {excel_file}")

if __name__ == '__main__':
    epd_id = "8be9edb5-c5b9-4be1-bfb8-b096f24a183b"
    
    # Fetch EPD and save JSON
    json_file = get_epd_by_id(epd_id)

    # Convert JSON to Excel
    convert_json_to_excel(json_file)
