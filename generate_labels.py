import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import re

# CONFIG
CSV_PATH = "items.csv" # CSV file with item names
BARCODE_DIR = "barcode_images" # Folder containing barcode images
LABEL_DIR = "static/labels" # Folder to save generated labels

# Label size in MILLIMETERS
LABEL_WIDTH_MM = 50
LABEL_HEIGHT_MM = 25
DPI = 300

# Layout
PADDING_MM = 0.5 # Padding around barcode
TEXT_HEIGHT_FRACTION = 1/3 # Bottom 1/3 for item name
TEXT_PADDING_H_MM = 2 # Horizontal padding for text
TEXT_PADDING_V_MM = 3 # Vertical padding for text in bottom third

# Font settings
FONT_PATH = "./monofonto rg.otf" # Use a valid TTF or OTF font
FONT_SIZE = 80 # Base font size (auto-scaled to fit width)

os.makedirs(LABEL_DIR, exist_ok=True)

# ——— Helpers ———
def mm_to_px(mm: float) -> int:
    #Convert millimeters to pixels based on DPI.
    return int((mm / 25.4) * DPI)

LABEL_WIDTH = mm_to_px(LABEL_WIDTH_MM)
LABEL_HEIGHT = mm_to_px(LABEL_HEIGHT_MM)
PADDING = mm_to_px(PADDING_MM)
TEXT_HEIGHT = int(LABEL_HEIGHT * TEXT_HEIGHT_FRACTION)
TEXT_PADDING_H = mm_to_px(TEXT_PADDING_H_MM)
TEXT_PADDING_V = mm_to_px(TEXT_PADDING_V_MM)

def sanitize_filename(name: str) -> str:
    # Remove illegal filename characters.
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

def get_text_size(draw, text, font):
    # Return width and height of the text in pixels.
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

# ——— Label Creation ———
def create_label(barcode_img_path: str, item_name: str, output_path: str):
    # Create a label image with barcode on top and item name in bottom 1/3.
    
    # Create a B/W image for the label
    label = Image.new("1", (LABEL_WIDTH, LABEL_HEIGHT), 1)

    # Add Barcode (top 2/3 of label)
    max_barcode_height = LABEL_HEIGHT - TEXT_HEIGHT - PADDING*2
    barcode_img = Image.open(barcode_img_path).convert("1")
    barcode_img = barcode_img.resize((LABEL_WIDTH - 2*PADDING, max_barcode_height), Image.LANCZOS)
    label.paste(barcode_img, (PADDING, PADDING))

    # Add Item Name (bottom 1/3 of label)
    draw = ImageDraw.Draw(label)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Measure text
    text_width, text_height = get_text_size(draw, item_name, font)
    
    # Auto-scale font horizontally to fit width minus horizontal padding
    max_width = LABEL_WIDTH - 2 * TEXT_PADDING_H
    if text_width > max_width:
        scale_factor = max_width / text_width
        scaled_font_size = max(int(FONT_SIZE * scale_factor), 1)
        font = ImageFont.truetype(FONT_PATH, scaled_font_size)
        text_width, text_height = get_text_size(draw, item_name, font)

    # Horizontal position: center
    text_x = (LABEL_WIDTH - text_width) // 2

    # Vertical position: center in bottom third minus vertical padding
    bottom_third_y = LABEL_HEIGHT - TEXT_HEIGHT
    text_y = bottom_third_y + (TEXT_HEIGHT - text_height) // 2
    text_y = max(text_y, bottom_third_y + TEXT_PADDING_V)  # apply vertical padding

    draw.text((text_x, text_y), item_name, font=font, fill=0)

    # Save the label
    label.save(output_path)
    print(f"🏷️  Created label: {output_path}")

def main():
    df = pd.read_csv(CSV_PATH)
    ITEM_COL = "Item Name"

    if ITEM_COL not in df.columns:
        raise ValueError(f"CSV must contain '{ITEM_COL}' column")

    for idx, row in df.iterrows():
        item_name = row[ITEM_COL]
        if pd.isna(item_name) or str(item_name).strip() == "":
            print(f"⚠️  Row {idx+1}: Missing item name — skipped")
            continue

        safe_name = sanitize_filename(str(item_name))
        barcode_img_path = os.path.join(BARCODE_DIR, f"{safe_name}.png")

        if not os.path.exists(barcode_img_path):
            print(f"❌ Barcode image not found: {barcode_img_path}")
            continue

        output_path = os.path.join(LABEL_DIR, f"{safe_name}_label.png")
        create_label(barcode_img_path, str(item_name), output_path)

    print("All labels created.")

if __name__ == "__main__":
    main()
