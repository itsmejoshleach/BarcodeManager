import os
import csv
import re
import requests
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Config
CSV_PATH = "./items.csv"

BARCODE_DIR = "static/barcode_images"
LABEL_DIR = "static/labels"
BARCODE_API = "https://barcodeapi.org/api/code128/{}"
FONT_PATH = "./monofonto rg.otf"

CSV_COLUMNS = [
    "Item Name",
    "Item Description / Alternate Names",
    "Barcode Number",
    "Barcode Image URL",
    "Barcode Image"
]

# Label config
LABEL_WIDTH_MM = 50
LABEL_HEIGHT_MM = 25
DPI = 300
TEXT_HEIGHT_FRACTION = 1 / 3
PADDING_MM = 0.5

# Setup
os.makedirs(BARCODE_DIR, exist_ok=True)
os.makedirs(LABEL_DIR, exist_ok=True)

def mm_to_px(mm):
    return int((mm / 25.4) * DPI)

LABEL_WIDTH = mm_to_px(LABEL_WIDTH_MM)
LABEL_HEIGHT = mm_to_px(LABEL_HEIGHT_MM)
PADDING = mm_to_px(PADDING_MM)
TEXT_HEIGHT = int(LABEL_HEIGHT * TEXT_HEIGHT_FRACTION)

# Functions
def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

def ensure_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_COLUMNS)

def load_items(query=""):
    ensure_csv()
    df = pd.read_csv(CSV_PATH).fillna("")

    if query:
        df = df[
            df["Item Name"].str.contains(query, case=False) |
            df["Item Description / Alternate Names"].str.contains(query, case=False) |
            df["Barcode Number"].astype(str).str.contains(query)
        ]

    items = []
    for _, row in df.iterrows():
        name = row["Item Name"].strip()
        if not name:
            continue

        safe = sanitize_filename(name)
        items.append({
            "name": name,
            "description": row["Item Description / Alternate Names"],
            "barcode": row["Barcode Number"],
            "label": f"labels/{safe}_label.png"
        })

    return items

# Barcode generation
def generate_barcode(barcode, item_name):
    safe = sanitize_filename(item_name)
    url = BARCODE_API.format(barcode)

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    path = os.path.join(BARCODE_DIR, f"{safe}.png")
    with open(path, "wb") as f:
        f.write(r.content)

    return path

# Label Generation
def create_label(barcode_img_path, item_name):
    safe = sanitize_filename(item_name)
    out_path = os.path.join(LABEL_DIR, f"{safe}_label.png")

    label = Image.new("1", (LABEL_WIDTH, LABEL_HEIGHT), 1)
    barcode = Image.open(barcode_img_path).convert("1")

    max_w = LABEL_WIDTH - 2 * PADDING
    max_h = LABEL_HEIGHT - TEXT_HEIGHT - 2 * PADDING

    bw, bh = barcode.size
    scale = min(max_w / bw, max_h / bh)
    barcode = barcode.resize((int(bw * scale), int(bh * scale)), Image.LANCZOS)

    label.paste(barcode, ((LABEL_WIDTH - barcode.width) // 2, PADDING))

    draw = ImageDraw.Draw(label)
    font_size = 80
    font = ImageFont.truetype(FONT_PATH, font_size)

    while draw.textbbox((0, 0), item_name, font=font)[2] > LABEL_WIDTH - 10:
        font_size -= 2
        font = ImageFont.truetype(FONT_PATH, font_size)

    bbox = draw.textbbox((0, 0), item_name, font=font)
    text_x = (LABEL_WIDTH - (bbox[2] - bbox[0])) // 2
    text_y = LABEL_HEIGHT - TEXT_HEIGHT + (TEXT_HEIGHT - (bbox[3] - bbox[1])) // 2

    draw.text((text_x, text_y), item_name, font=font, fill=0)
    label.save(out_path)

# Web App Routes
@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    if request.method == "POST":
        query = request.form.get("search", "").strip()
    items = load_items(query)
    return render_template("index.html", items=items, query=query)

@app.route("/add", methods=["POST"])
def add_item():
    name = request.form.get("name", "").strip()
    desc = request.form.get("description", "").strip()
    barcode = request.form.get("barcode", "").strip()

    if not name or not barcode:
        return "Missing fields", 400

    ensure_csv()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([name, desc, barcode, "", ""])

    barcode_path = generate_barcode(barcode, name)
    create_label(barcode_path, name)

    return redirect(url_for("index"))

# Run the thing
if __name__ == "__main__":
    ensure_csv()
    app.run(debug=True, host='0.0.0.0')
