import random
import pandas as pd
from specklepy.api.credentials import get_default_account
from specklepy.transports.server import ServerTransport
from specklepy.api.client import SpeckleClient
from specklepy.api import operations
from specklepy.objects.base import Base

# Identify the Project and Model
project_id = "f6fd1ebba3"
model_id = "29f596e9d7"

# Set up authentication and connection to Speckle server
client = SpeckleClient(host="https://macad.speckle.xyz")
account = get_default_account()
client.authenticate_with_account(account)

# Get specific Model by ID
my_model = client.model.get(model_id, project_id)
print(f"Model: {my_model.name}")

# Get the latest version's Referenced Object ID
versions = client.version.get_versions(model_id, project_id)
if not versions.items:
    print("No versions found.")
    exit()

latest_version = versions.items[0]
referenced_obj_id = latest_version.referencedObject

# Receive the referenced object (Speckle data)
print("Fetching data from the server...")
transport = ServerTransport(project_id, client)
objData = operations.receive(referenced_obj_id, transport)
print("Got the data!")

# Dictionary to store materials and their random emission factors (kg CO2/m³)
carbon_emissions = {}

# Set to track processed IDs (to avoid duplicates)
processed_ids = set()

# List to store extracted element data
elements_data = []

# Function to extract object properties (handling standard & adaptive families)
def extract_data(obj, parent_family=None):
    if isinstance(obj, Base):
        obj_id = getattr(obj, "id", None)

        # Skip duplicates
        if obj_id in processed_ids or obj_id is None:
            return
        processed_ids.add(obj_id)

        # Extract key properties
        obj_name = getattr(obj, "name", None) or getattr(obj, "applicationId", None)
        family = getattr(obj, "family", None) or parent_family
        volume = getattr(obj, "volume", None)
        material_name = "Unknown Material"

        # Convert parameters if it's a Base object
        parameters = getattr(obj, "parameters", {})
        if isinstance(parameters, Base):
            parameters = parameters.__dict__  # Convert Base object to dictionary

        # If name is missing, try extracting from parameters
        if obj_name is None and isinstance(parameters, dict):
            for key, value in parameters.items():
                if "name" in key.lower():
                    obj_name = getattr(value, "value", "Unnamed Object")  # Fix applied
        
        # If still missing, use family as last resort
        if obj_name is None:
            obj_name = family if family else "Unnamed Object"

        # Extract material from parameters
        if isinstance(parameters, dict):
            for key, value in parameters.items():
                if "material" in key.lower():
                    material_name = getattr(value, "value", "Unknown Material")  # Fix applied
        
        # If family is missing, check parameters
        if not family:
            for key, value in parameters.items():
                if "family" in key.lower():
                    family = getattr(value, "value", "Unknown Family")  # Fix applied

        # Special case: Adaptive families (extract from materialQuantities)
        material_quantities = getattr(obj, "materialQuantities", None)
        if isinstance(material_quantities, list):
            for mq in material_quantities:
                if isinstance(mq, Base):
                    mq_id = getattr(mq, "id", "Unknown ID")
                    mq_volume = getattr(mq, "volume", None)
                    mq_material = getattr(mq, "material", None)

                    # Ensure material name is extracted correctly
                    if isinstance(mq_material, Base):
                        mq_material = getattr(mq_material, "name", "Unknown Material")

                    # Only store if volume is valid
                    if mq_volume and mq_volume > 0 and mq_id not in processed_ids:
                        processed_ids.add(mq_id)

                        if mq_material not in carbon_emissions:
                            carbon_emissions[mq_material] = random.uniform(50, 500)  # Random kg CO₂/m³

                        emission_factor = carbon_emissions[mq_material]
                        total_emissions = mq_volume * emission_factor

                        elements_data.append({
                            "ID": mq_id,
                            "Object Name": obj_name,
                            "Family": family if family else "Unknown Family",
                            "Material": mq_material if mq_material else "Unknown Material",
                            "Volume (m³)": mq_volume,
                            "Emission Factor (kg CO₂/m³)": emission_factor,
                            "Total Carbon Footprint (kg CO₂)": total_emissions
                        })

        # Store only normal objects with volume
        elif volume and volume > 0:
            if material_name not in carbon_emissions:
                carbon_emissions[material_name] = random.uniform(50, 500)  # Random kg CO₂/m³

            emission_factor = carbon_emissions[material_name]
            total_emissions = volume * emission_factor

            elements_data.append({
                "ID": obj_id,
                "Object Name": obj_name,
                "Family": family if family else "Unknown Family",
                "Material": material_name,
                "Volume (m³)": volume,
                "Emission Factor (kg CO₂/m³)": emission_factor,
                "Total Carbon Footprint (kg CO₂)": total_emissions
            })

        # Recursively check nested objects
        for key in obj.get_member_names():
            extract_data(getattr(obj, key), parent_family=family)
    
    elif isinstance(obj, list):
        for item in obj:
            extract_data(item, parent_family)

# Extract elements from the received Speckle object
if hasattr(objData, "elements"):
    for element in objData.elements:
        extract_data(element)

# Now, elements_data is ready to be used directly in speckle_epd_carbon
print("✅ Extracted materials and volumes are ready for EPD processing!")

# # Print extracted materials
# extracted_materials = sorted(set([item['Material'] for item in elements_data]))
# print("📦 Extracted Materials:")
# for material in extracted_materials:
#     print(f" - {material}")