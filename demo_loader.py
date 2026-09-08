"""
Loads bundled demo/ files into the session state uploads dicts so
'RUN INDUSTRIAL DEMO' works with a single click.
"""
import os
from config import settings
from core import state_manager as sm

DEMO_FILES = {
    "pdfs": ["inspection_report.pdf", "maintenance_manual.pdf"],
    "images": ["equipment_image.jpg"],
    "csv": ["sensor_data.csv"],
}


def load_demo_files():
    for name in DEMO_FILES["pdfs"]:
        src = os.path.join(settings.DEMO_DIR, name)
        if os.path.exists(src):
            sm.get("uploaded_pdfs")[name] = src
    for name in DEMO_FILES["images"]:
        src = os.path.join(settings.DEMO_DIR, name)
        if os.path.exists(src):
            sm.get("uploaded_images")[name] = src
    for name in DEMO_FILES["csv"]:
        src = os.path.join(settings.DEMO_DIR, name)
        if os.path.exists(src):
            sm.get("uploaded_csvs")[name] = src
