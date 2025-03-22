import os
import json
import re
import pandas as pd
from shared import get_epds
from fetch_epd import get_epd_by_id  
from extract_epd_values import extract_corrected_lcia_co2_values_ignore_D

# Ensure the directory exists
JSON_SAVE_PATH = "./my_collaborative/json_files/"
os.makedirs(JSON_SAVE_PATH, exist_ok=True)

def parse_epd_list(data: dict):
    """Parses EPD data and returns a list of (name, UUID) tuples."""
    return [(epd.get("name"), epd.get("uuid")) for epd in data.get("data", [])]

def find_material(materials, material_type):
    """Finds all matching materials based on keywords."""
    material_keywords = {
        "Aluminum": [r'Aluminium', r'Aluminiumblech', r'Aluminiumfolie', r'Aluminiumprofil pressblank', r'Aluminum', r'GEN_Aluminium', r'GEN_Aluminium \d+'],
        "Wood": [r'Holz', r'Massivholz', r'Furnier'],
        "Glass": [r'Glas', r'Floatglas', r'Verbundglas', r'Isolierglas'],
        "Steel": [r'Stahl', r'Baustahl', r'Edelstahl', r'Stahlblech'],
        "Copper": [r'Kupfer', r'Kupferblech', r'Kupferrohr'],
        "PV": [r'Photovoltaik', r'Solarmodul', r'PV-Modul', r'PV Panel']
    }

    if material_type not in material_keywords:
        print(f"Material type '{material_type}' not supported.")
        return []

    pattern = re.compile('|'.join(material_keywords[material_type]), re.IGNORECASE)
    matches = [material for material in materials if pattern.search(material[0])]
    return matches

def list_epds(material_type="Aluminum"):
    """Lists EPDs in the Ökobau database and fetches the best EPD with valid GWP > 1."""
    data = get_epds()
    materials_list = parse_epd_list(data)
    candidates = find_material(materials_list, material_type)

    for name, uuid in candidates:
        print(f"Trying EPD match: {name} (UUID: {uuid})")
        json_data = get_epd_by_id(uuid)

        if not json_data:
            continue

        file_path = os.path.join(JSON_SAVE_PATH, f"{uuid}.json")
        json_data["materialType"] = material_type

        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)

        print(f"✅ EPD JSON file saved: {file_path}")

        epd_result = extract_corrected_lcia_co2_values_ignore_D(file_path)
        gwp = epd_result.get("Total Carbon Footprint (kg CO₂ eq.) (Excluding D)", 0)

        if gwp and gwp > 1:
            return file_path

        print(f"⚠️ Skipping EPD with GWP = {gwp}")

    print("❌ No EPDs with valid GWP data found.")
    return None
