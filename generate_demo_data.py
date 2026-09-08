"""
One-off script to generate synthetic demo data for the hackathon demo:
- inspection_report.pdf
- maintenance_manual.pdf
- sensor_data.csv
- equipment_image.jpg (synthetic, no external assets)

Run: python demo/generate_demo_data.py
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFilter
import pandas as pd

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))


def make_pdf(filename, title, paragraphs):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4
    y = 60
    page.insert_text((50, y), title, fontsize=18, fontname="helv")
    y += 40

    for para_group in paragraphs:
        for para in para_group:
            lines_needed = max(1, len(para) // 90 + 1)
            block_height = 16 * lines_needed + 12
            if y + block_height > 780:
                page = doc.new_page(width=595, height=842)
                y = 60
            rect = fitz.Rect(50, y, 545, y + block_height + 10)
            page.insert_textbox(rect, para, fontsize=11, fontname="helv")
            y += block_height

    doc.save(os.path.join(DEMO_DIR, filename))
    doc.close()
    print(f"Created {filename}")


def make_inspection_report():
    paragraphs = [
        [
            "INSPECTION REPORT — PUMP UNIT PU-204",
            "Facility: MRPL Industrial Site B | Inspector: J. Rao | Date: 2026-08-14",
            "",
            "1. SUMMARY OF FINDINGS",
            "Routine inspection of centrifugal pump unit PU-204 was conducted as part of the "
            "quarterly maintenance cycle. The unit showed elevated operating temperature during "
            "the final hour of continuous operation, along with intermittent vibration spikes "
            "recorded by the onboard sensor array. No active leakage was observed at the time of "
            "inspection, though minor surface discoloration was noted near the housing seal.",
            "",
            "2. OBSERVATIONS",
            "- Bearing housing temperature trending upward over the past 72 hours of operation.",
            "- Vibration readings intermittently exceeded baseline by approximately 15-20%.",
            "- Discoloration observed on the lower housing, consistent with historical minor "
            "seepage in similar units, though not confirmed as active leakage.",
            "- Coupling alignment within tolerance; no immediate mechanical fault visible.",
            "",
            "3. INSPECTOR RECOMMENDATION",
            "Recommend correlating sensor trend data with maintenance manual thresholds and "
            "scheduling a follow-up inspection within 5 operating days. Continuous monitoring "
            "advised until root cause of temperature trend is confirmed.",
        ],
    ]
    make_pdf("inspection_report.pdf", "PUMP UNIT PU-204 — INSPECTION REPORT", paragraphs)


def make_maintenance_manual():
    paragraphs = [
        [
            "MAINTENANCE MANUAL — PUMP UNIT PU-200 SERIES",
            "Document Ref: MM-PU200-REV3 | Issued by: Engineering Standards Group",
            "",
            "SECTION 4: OPERATING PARAMETERS AND THRESHOLDS",
            "The PU-200 series centrifugal pump is rated for continuous operation within the "
            "following envelope. Operation outside these limits requires inspection before "
            "continued use.",
            "",
            "4.1 Temperature",
            "Recommended operating temperature range for the bearing housing is 40°C to 90°C. "
            "Sustained readings above 90°C indicate possible bearing wear, lubrication "
            "degradation, or cooling system fault and require inspection within 48 hours.",
            "",
            "4.2 Vibration",
            "Normal vibration range is 0 to 6.0 mm/s RMS. Levels sustained above this threshold "
            "may indicate misalignment, bearing damage, or impeller imbalance and should be "
            "investigated before the next operating cycle.",
            "",
            "4.3 Pressure",
            "Discharge pressure should remain within 8 to 12 bar under normal load. Pressure "
            "excursions above 12 bar should be logged and reviewed against system demand.",
            "",
            "SECTION 7: SEAL AND HOUSING CONDITION",
            "Minor surface discoloration around the housing seal is common and does not by "
            "itself indicate failure. However, discoloration combined with elevated temperature "
            "or vibration readings should prompt a combined visual and sensor-based assessment "
            "before the unit is returned to unattended continuous operation.",
            "",
            "SECTION 9: RECOMMENDED ACTION MATRIX",
            "If temperature AND vibration both exceed threshold: schedule inspection within 48 "
            "hours and prepare for possible bearing replacement.",
            "If only one parameter exceeds threshold: increase monitoring frequency and "
            "re-evaluate within 5 operating days.",
            "If no parameters exceed threshold: continue standard quarterly inspection cycle.",
        ],
    ]
    make_pdf("maintenance_manual.pdf", "PU-200 SERIES — MAINTENANCE MANUAL", paragraphs)


def make_sensor_csv():
    rng = np.random.default_rng(42)
    n = 96  # 96 readings (e.g. every 30 min over 48 hours)
    timestamps = pd.date_range("2026-08-12 00:00", periods=n, freq="30min")

    # Baseline normal ranges, with a drift/spike in the last ~20% to simulate the
    # abnormal condition described in the inspection report.
    temperature = np.concatenate([
        rng.normal(72, 3, int(n * 0.75)),
        np.linspace(78, 97, int(n * 0.25)) + rng.normal(0, 2, int(n * 0.25)),
    ])
    pressure = rng.normal(10, 0.6, n)
    vibration = np.concatenate([
        rng.normal(3.2, 0.5, int(n * 0.75)),
        np.linspace(3.5, 7.4, int(n * 0.25)) + rng.normal(0, 0.4, int(n * 0.25)),
    ])
    rpm = rng.normal(2950, 60, n)

    df = pd.DataFrame({
        "timestamp": timestamps.astype(str),
        "temperature": np.round(temperature, 1),
        "pressure": np.round(pressure, 2),
        "vibration": np.round(vibration, 2),
        "rpm": np.round(rpm, 0),
    })
    path = os.path.join(DEMO_DIR, "sensor_data.csv")
    df.to_csv(path, index=False)
    print(f"Created sensor_data.csv ({len(df)} rows)")


def make_equipment_image():
    """Synthetic equipment-like image (no external/copyrighted assets)."""
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (60, 64, 70))
    draw = ImageDraw.Draw(img)

    # Simple pump-like silhouette: cylindrical housing + base
    draw.rectangle([250, 180, 550, 420], fill=(110, 115, 122), outline=(30, 30, 30), width=4)
    draw.ellipse([230, 180, 290, 420], fill=(100, 105, 112), outline=(30, 30, 30), width=4)
    draw.rectangle([180, 420, 620, 470], fill=(70, 72, 78), outline=(20, 20, 20), width=3)  # base

    # Bolts
    for bx in [270, 330, 470, 530]:
        draw.ellipse([bx - 6, 190, bx + 6, 202], fill=(40, 40, 40))

    # Simulated discoloration / staining near housing seam (matches inspection report)
    stain = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    stain_draw = ImageDraw.Draw(stain)
    stain_draw.ellipse([300, 380, 420, 430], fill=(70, 50, 30, 120))
    stain = stain.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), stain).convert("RGB")

    # Add some texture/noise for edge-detection to pick up
    arr = np.array(img).astype(np.int16)
    noise = np.random.default_rng(1).integers(-8, 8, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    path = os.path.join(DEMO_DIR, "equipment_image.jpg")
    img.save(path, quality=90)
    print("Created equipment_image.jpg")


if __name__ == "__main__":
    make_inspection_report()
    make_maintenance_manual()
    make_sensor_csv()
    make_equipment_image()
    print("Demo data generation complete.")
