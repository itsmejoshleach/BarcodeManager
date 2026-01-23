import os
import requests
import pandas as pd
import re

# Config
CSV_PATH = "items.csv"
OUTPUT_DIR = "static/barcode_images"
URL_TEMPLATE = "https://barcodeapi.org/api/code128/{}"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    #Remove characters that are invalid in filenames.
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    return name

def download_barcode_image(barcode: str, item_name: str) -> bool:
    #Download the barcode image for a given barcode.
    # Format barcode with 2 decimal places
    try:
        barcode_float = float(barcode)
        barcode_str = f"{barcode_float:.2f}"
    except ValueError:
        barcode_str = str(barcode).strip()

    url = URL_TEMPLATE.format(barcode_str)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        safe_name = sanitize_filename(item_name)
        file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.png")

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Saved: {file_path}")
        return True

    except requests.RequestException as e:
        print(f"❌ Failed to download '{barcode_str}': {e}")
        return False


def main():
    df = pd.read_csv(CSV_PATH)

    BARCODE_COL = "Barcode Number"
    ITEM_COL = "Item Name"

    missing_cols = [c for c in [BARCODE_COL, ITEM_COL] if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"CSV must contain columns: {missing_cols}. "
            f"Found columns: {list(df.columns)}"
        )

    print(f"Found {len(df)} rows — starting download...")

    for idx, row in df.iterrows():
        barcode = row[BARCODE_COL]
        item_name = row[ITEM_COL]

        # Skip missing / empty barcodes
        if pd.isna(barcode) or str(barcode).strip() == "":
            print(f"⚠️  Row {idx + 1}: No barcode value — skipped")
            continue

        # Fallback if item name is missing
        if pd.isna(item_name) or str(item_name).strip() == "":
            item_name = str(barcode).strip()

        download_barcode_image(
            barcode=barcode,
            item_name=str(item_name)
        )

    print("Done.")


if __name__ == "__main__":
    main()
