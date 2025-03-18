import re
import pandas as pd
from shared import get_epds
from fetch_epd import get_epd_by_id

def parse_epd_list(data: dict):
    """Parses EPD data and returns a list of (name, UUID) tuples."""
    return [(epd.get("name"), epd.get("uuid")) for epd in data.get("data", [])]

def find_material(materials, material_type):
    """
    Finds the best match for the specified material type from a list of materials with UUIDs.
    
    Parameters:
        materials (list of tuples): List of (name, UUID) tuples.
        material_type (str): The type of material to search for (e.g., 'Aluminum', 'Wood', 'Glass', 'Steel', 'Copper').
        
    Returns:
        tuple: The best matching material (name, UUID) or None if not found.
    """
    material_keywords = {
        "Aluminum": [r'\bAluminiumblech\b', r'\bAluminiumfolie\b', r'\bAluminiumprofil pressblank\b'],
        "Wood": [r'\bHolz\b', r'\bMassivholz\b', r'\bFurnier\b'],
        "Glass": [r'\bGlas\b', r'\bFloatglas\b', r'\bVerbundglas\b', r'\bIsolierglas\b'],
        "Steel": [r'\bStahl\b', r'\bBaustahl\b', r'\bEdelstahl\b', r'\bStahlblech\b'],
        "Copper": [r'\bKupfer\b', r'\bKupferblech\b', r'\bKupferrohr\b']
    }
    
    if material_type not in material_keywords:
        print(f"Material type '{material_type}' not supported.")
        return None
    
    # Compile regex pattern for efficiency
    pattern = re.compile('|'.join(material_keywords[material_type]), re.IGNORECASE)
    
    # Find the first matching material
    for material in materials:
        if pattern.search(material[0]):
            return material  # Return only the first match
    
    return None

def list_epds(material_type="Aluminum"):
    """Lists EPDs in the Ökobau database and fetches the EPD for the closest match to the specified material type."""
    data = get_epds()
    materials_list = parse_epd_list(data)
    
    # Find the best match to the specified material type
    best_match = find_material(materials_list, material_type)
    
    if best_match:
        name, uuid = best_match
        print(f"Match: {name} (UUID: {uuid})")
        json_file = get_epd_by_id(uuid)  # Fetch and save EPD data
        print(f"EPD JSON file saved: {json_file}")
    else:
        print("No matching material found.")

if __name__ == "__main__":
    material_type = input("Enter material type (Aluminum, Wood, Glass, Steel, Copper): ")
    list_epds(material_type)
