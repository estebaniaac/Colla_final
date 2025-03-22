Perfect! Here's an updated `README.md` including the **collaborative BIM** academic context from IAAC:

---

# ♻️ Speckle Carbon Matcher

A Python-based app that extracts material volumes from Revit models via Speckle, matches them to **Oekobaudat EPDs**, and computes the **total embodied carbon footprint**. The results are pushed back to Speckle for direct BIM integration and visualization.

> 🧠 **Created for the subject _Collaborative BIM_ within the Master in Advanced Computation for Architecture and Design (MaCAD) at IAAC.**

---

## 🌍 Why this matters

Designing for sustainability starts with **awareness**—this tool automates the extraction and mapping of material data from BIM to calculate embodied carbon, making it easier to inform eco-conscious decisions early in the design process.

---

## 🚀 Features

- 🔌 **Connects to Speckle** to fetch Revit geometry and material data.
- 📏 Extracts volumes and material names (including adaptive components).
- 🌿 Matches materials with **Oekobaudat EPDs** via fuzzy logic.
- 📊 Calculates embodied carbon (kg CO₂) using A1-A3 `GWP-total` values.
- 🧮 Exports results to Excel and re-injects carbon data into Speckle for visualization.

---

## 📂 File Structure

```
.
├── specklecarbonfootprint.py       # Fetches geometry + material info from Speckle
├── fetch_epd.py                    # Downloads and prepares Oekobaudat dataset
├── extract_epd_values.py           # Extracts GWP values from EPD entries
├── find_closer_material.py         # Finds closest EPDs to project materials
├── speckle_epd_carbon.py           # Full pipeline: match, compute, export
├── send_to_speckle.py              # Main entry: triggers computation, writes to Speckle
├── shared.py                       # Utility functions (unit conversion, cleaning)
└── Speckle_EPD_Carbon_Footprint.xlsx  # Output report with results
```

---

## 🧠 About the Data

- Based on **Oekobaudat** (https://oekobaudat.de), a publicly available German database of environmental product declarations.
- The app focuses on `A1-A3 GWP-total` (Global Warming Potential) indicators.
- EPDs with volumetric units (kg CO₂/m³) are prioritized for accurate matching.
- Uses fuzzy string matching to find the **closest EPD** when no exact match is found.

---

## 📈 Output

| Element ID | Material | Volume (m³) | Emission Factor (kg CO₂/m³) | Total Carbon (kg CO₂) |
|------------|----------|-------------|-------------------------------|------------------------|
| 3a8ef...   | Concrete | 2.3         | 295.3                         | 679.2                  |

These are shown both in an Excel file and within the Speckle web interface as element properties.

---

## ✅ Prerequisites

- Python 3.9+
- Speckle stream containing Revit model data
- Dependencies (install with pip):

```bash
pip install specklepy pandas fuzzywuzzy openpyxl
```

---

## ▶️ Run

Run the full pipeline:

```bash
python send_to_speckle.py
```

This will:
- Trigger the full EPD computation
- Update Excel
- Send carbon info back to Speckle
- Create a new model version

---

## ☁️ Cloud Deployment (optional)

You can deploy the script to `fly.io` for remote execution. Useful if you want collaborators to trigger carbon updates without local setup.

_Ask for a `fly.toml` if needed._

---

## 📌 Limitations

- Only processes elements with valid `volume` and `material` data
- EPD matching is name-based, not category-based (for now)
- Graphical visualization in Speckle UI is limited to property fields

---

## 🎓 Credits

Developed as part of the **Collaborative BIM** course  
**Master in Advanced Computation for Architecture and Design (MaCAD)**  
**[Institute for Advanced Architecture of Catalonia (IAAC)](https://iaac.net/)**

