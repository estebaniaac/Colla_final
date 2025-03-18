import json
import pandas as pd
import os
from find_closer_material import list_epds

def extract_values_from_json(json_file):
    """
    Extracts product name and specified values from a JSON file.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract product name
    product_name = data.get("processInformation", {}).get("dataSetInformation", {}).get("name", {}).get("baseName", [{}])[0].get("value", "Unknown Product")
    
    # Extract values for A1-A5, C1-C4, and D
    values = {
        "A1-A3": None,
        "A4": None,
        "A5": None,
        "C1": None,
        "C2": None,
        "C3": None,
        "C4": None,
        "D": None
    }
    
    for result in data.get("LCIAResults", {}).get("LCIAResult", []):
        for value in result.get("other", {}).get("anies", []):
            if "module" in value and "value" in value:
                module = value["module"]
                if module in values:
                    values[module] = float(value["value"])
    
    return {"Product Name": product_name, **values}

def process_json_files(folder_path, output_excel):
    """
    Processes all JSON files in a folder and saves the extracted values into an Excel file.
    """
    extracted_data = []
    
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            json_file = os.path.join(folder_path, file)
            extracted_data.append(extract_values_from_json(json_file))
    
    df = pd.DataFrame(extracted_data)
    df.to_excel(output_excel, index=False)
    print(f"Data saved to {output_excel}")

if __name__ == "__main__":
    material_type = input("Enter material type (Aluminum, Wood, Glass, Steel, Copper): ")
    list_epds(material_type)  # Fetches the JSON file based on material type
    
    folder_path = "./src/json_files"  # Replace with the actual folder path containing JSON files
    output_excel = "./extracted_epd_values.xlsx"
    process_json_files(folder_path, output_excel)