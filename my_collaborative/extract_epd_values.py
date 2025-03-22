import json
import os
import pandas as pd

def extract_corrected_lcia_co2_values_ignore_D(json_file):
    """
    Extracts CO2-equivalent values correctly from LCIAResults, excluding Module D.
    Ensures correct summation of all relevant GWP values (A, B, C modules only).
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)  # Load JSON as dictionary
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Failed to load JSON from {json_file}: {e}")
            return None  

    if not isinstance(data, dict):
        print(f"❌ ERROR: JSON data in {json_file} is not a dictionary. Skipping.")
        return None

    # Extract product name
    try:
        product_name = data.get("processInformation", {}).get("dataSetInformation", {}).get("name", {}).get("baseName", [{}])[0].get("value", "Unknown Product")
    except Exception:
        product_name = "Unknown Product"

    # Extract material type from stored JSON metadata
    material_name = data.get("processInformation", {}).get("dataSetInformation", {}).get("classificationInformation", {}).get("classification", [{}])[0].get("class", [{}])[-1].get("value", "Unknown Material")

    # Extract values from LCIAResults, ignoring Module D
    total_carbon_footprint = 0
    extracted_co2_values = []

    try:
        for lcia_result in data.get("LCIAResults", {}).get("LCIAResult", []):
            method_description = lcia_result.get("referenceToLCIAMethodDataSet", {}).get("shortDescription", [{}])[0].get("value", "")
            if "Global Warming Potential" in method_description:
                for entry in lcia_result.get("other", {}).get("anies", []):
                    if isinstance(entry, dict) and "value" in entry and "module" in entry:
                        module = entry["module"]
                        if not module.startswith("D"):  # Exclude Module D
                            try:
                                value = float(entry["value"])
                                extracted_co2_values.append({"module": module, "value": value})
                                total_carbon_footprint += value
                            except ValueError:
                                print(f"⚠️ Warning: Could not convert value {entry['value']} in {json_file}")
    except Exception as e:
        print(f"❌ ERROR: Failed to extract CO₂-equivalent values from {json_file}: {e}")

    return {
        "Product Name": product_name,
        "Material Name": material_name,
        "Total Carbon Footprint (kg CO₂ eq.) (Excluding D)": total_carbon_footprint,
        "Extracted CO₂ Values (Excluding D)": extracted_co2_values
    }

def process_json_files(folder_path, output_excel):
    """
    Processes all JSON files in a folder, extracts CO₂ data, and saves it to an Excel file.
    """
    extracted_data = []

    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            json_file = os.path.join(folder_path, file)
            epd_data = extract_corrected_lcia_co2_values_ignore_D(json_file)
            if epd_data:  # Only append if extraction was successful
                extracted_data.append(epd_data)

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        df.to_excel(output_excel, index=False)
        print(f"✅ Data saved to {output_excel}")
    else:
        print("⚠️ No valid data extracted.")

if __name__ == "__main__":
    folder_path = "./my_collaborative/json_files"  # Path to JSON storage
    output_excel = "./extracted_epd_values_no_D.xlsx"
    process_json_files(folder_path, output_excel)
