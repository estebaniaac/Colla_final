import os
import pandas as pd
import re
from find_closer_material import list_epds
from extract_epd_values import extract_corrected_lcia_co2_values_ignore_D
from specklecarbonfootprint import elements_data

# Function to extract basic material name
# Print simplified (basic) materials extracted
def extract_basic_material(material_name):
    material_name = material_name.lower()
    
    if "aluminium" in material_name or "aluminum" in material_name:
        return "Aluminum"
    if "steel" in material_name:
        return "Steel"
    if "wood" in material_name or "holz" in material_name:
        return "Wood"
    if "glass" in material_name or "glas" in material_name:
        return "Glass"
    if "copper" in material_name or "kupfer" in material_name:
        return "Copper"
    if "pv" in material_name or "photovoltaik" in material_name:
        return "PV"
    
    return "Unknown"


simplified_materials = sorted(set(extract_basic_material(item["Material"]) for item in elements_data if extract_basic_material(item["Material"]) != "Unknown"))
print("🔹 Simplified (Basic) Materials:")
for sm in simplified_materials:
    print(f" - {sm}")

# Step 1: Extract unique simplified materials
unique_materials = set()
for row in elements_data:
    basic_material = extract_basic_material(row["Material"])
    if basic_material != "Unknown":
        unique_materials.add(basic_material)

# Step 2: Match each simplified material with EPD and extract emission factor
material_epd_mapping = {}

for material in unique_materials:
    print(f"🔍 Searching for EPD match for material: {material}")
    epd_uuid = list_epds(material)
    
    if epd_uuid:
        print(f"✅ Found EPD UUID: {epd_uuid} for material: {material}")
        epd_data = extract_corrected_lcia_co2_values_ignore_D(epd_uuid)
        # print(epd_data)


        if epd_data and "Total Carbon Footprint (kg CO₂ eq.) (Excluding D)" in epd_data:
            emission_factor = epd_data["Total Carbon Footprint (kg CO₂ eq.) (Excluding D)"]

            material_epd_mapping[material] = emission_factor
        else:
            print(f"❌ EPD data for {material} missing GWP info.")
            material_epd_mapping[material] = None
    else:
        print(f"❌ No matching EPD found for material: {material}")
        material_epd_mapping[material] = None

# Step 3: Apply emission factors to the Speckle elements
df = pd.DataFrame(elements_data)
print("✅ Loaded extracted material data for EPD matching.")

for index, row in df.iterrows():
    basic_material = extract_basic_material(row["Material"])
    volume = row["Volume (m³)"]

    if basic_material in material_epd_mapping:
        emission_factor = material_epd_mapping[basic_material]
        if emission_factor is not None:
            total_footprint = volume * emission_factor
            df.at[index, "Emission Factor (kg CO₂/m³)"] = emission_factor
            df.at[index, "Total Carbon Footprint (kg CO₂)"] = total_footprint
        else:
            df.at[index, "Emission Factor (kg CO₂/m³)"] = float("nan")
            df.at[index, "Total Carbon Footprint (kg CO₂)"] = float("nan")
    else:
        df.at[index, "Emission Factor (kg CO₂/m³)"] = float("nan")
        df.at[index, "Total Carbon Footprint (kg CO₂)"] = float("nan")

# Step 4: Export to Excel
excel_path = "Speckle_EPD_Carbon_Footprint.xlsx"
df.to_excel(excel_path, index=False)
print(f"✅ Final carbon footprint results saved to {excel_path}")
