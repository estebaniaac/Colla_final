import os
import json
import re
import pandas as pd
import subprocess
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.objects.base import Base
from specklepy.core.api.inputs.version_inputs import CreateVersionInput
from specklepy.serialization.base_object_serializer import BaseObjectSerializer

# ✅ Trigger the EPD calculation script
subprocess.run(["python", "./my_collaborative/speckle_epd_carbon.py"], check=True)

# ✅ Load the output Excel file
excel_path = "Speckle_EPD_Carbon_Footprint.xlsx"
df = pd.read_excel(excel_path)
df.columns = df.columns.str.strip().str.lower()  # Normalize column names
print(f"✅ Loaded {len(df)} elements from Excel. Columns: {df.columns.tolist()}")

# Speckle configuration
SPECKLE_HOST = "https://macad.speckle.xyz"
PROJECT_ID = "f6fd1ebba3"  # Project ID
MODEL_ID = "29f596e9d7"    # Model ID

# Connect to Speckle
account = get_default_account()
client = SpeckleClient(host=SPECKLE_HOST)
client.authenticate_with_account(account)
print(f"🔐 Authenticated as: {account.userInfo.email}")

# Prepare transport
transport = ServerTransport(client=client, account=account, stream_id=PROJECT_ID)

# 🔁 Fetch the latest version object from the model
model_with_versions = client.model.get_with_versions(model_id=MODEL_ID, project_id=PROJECT_ID)
model_versions = model_with_versions.versions.items

if model_versions:
    latest_version = model_versions[0]
    latest_obj_id = getattr(latest_version, "referencedObject", None)
    print(f"📥 Fetched latest referenced object: {latest_obj_id}")
    if latest_obj_id:
        existing_obj = operations.receive(latest_obj_id, transport)
        # 🔎 Save Speckle object structure to inspect IDs
        serializer = BaseObjectSerializer()
        json_str, _ = serializer.write_json(existing_obj)
        with open("speckle_object_structure.json", "w") as f:
            f.write(json_str)
        print("🧩 Speckle object structure saved to speckle_object_structure.json")
    else:
        print("⚠️ No referencedObject found in the latest version.")
        existing_obj = Base()
else:
    print("⚠️ No previous versions found. Starting with a fresh object.")
    existing_obj = Base()

# ✅ Attach carbon data to matching elements recursively
def find_all_elements_with_ids(base_obj):
    found = []

    def recurse(obj):
        if isinstance(obj, Base):
            obj_id = getattr(obj, "id", None)
            if obj_id:
                found.append(obj)
            for member_name in obj.get_member_names():
                try:
                    recurse(getattr(obj, member_name))
                except Exception:
                    pass
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(base_obj)
    return found

all_elements = find_all_elements_with_ids(existing_obj)
df["id"] = df["id"].astype(str).str.strip()
updated_count = 0

# Columns to skip to avoid conflicts
SKIP_COLUMNS = ["id", "material"]

for elem in all_elements:
    elem_id = str(getattr(elem, "id", "")).strip()
    match = df[df["id"] == elem_id]
    if not match.empty:
        print(f"🔗 Matched element ID: {elem_id}")
        row = match.iloc[0]
        for col in df.columns:
            if col.lower() not in SKIP_COLUMNS:
                clean_col = col.replace(" ", "_").replace(".", "_").replace("/", "_")
                try:
                    setattr(elem, clean_col, row[col])
                except Exception as e:
                    print(f"⚠️ Skipped setting {clean_col} on {elem_id}: {e}")
        updated_count += 1
    else:
        pass

print(f"✅ Updated {updated_count} elements with carbon data.")

# Send merged object back to Speckle
object_id = operations.send(base=existing_obj, transports=[transport])
print(f"📤 Sent object to Speckle. Object ID: {object_id}")

# Create a new version
version_data = CreateVersionInput(objectId=object_id, modelId=MODEL_ID, projectId=PROJECT_ID)
client.version.create(version_data)
print("✅ Version created successfully.")
