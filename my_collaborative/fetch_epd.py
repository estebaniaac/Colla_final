import json
import pandas as pd
from shared import get_full_epd

def get_epd_by_id(uuid: str):
    """Fetches the data of a specific EPD given its UUID and saves it to a JSON file."""
    data = get_full_epd(uuid)

    # Save JSON data to a file
    json_file = f"epd_{uuid}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"EPD data has been saved to {json_file}")

    return json_file  # Return the filename for further processing

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
