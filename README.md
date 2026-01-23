# Barcode Label Generator

This project generates printable barcode labels from a CSV file.  
It works in **three stages**:

1. Download barcode images from an API  
2. Generate label images with barcodes + item names  
3. Combine all labels into a single PDF for printing.
    - Please note you can also select which labels to print by printing the label images directly.

Designed for high-DPI label printers and inventory-style workflows.

---

## Project Structure

.
├── items.csv # Input CSV file
├── barcode_images/ # Downloaded barcode PNGs
├── labels/ # Generated label PNGs
├── labels.pdf # Final combined PDF
├── download_barcodes.py # Script 1: Download barcodes
├── create_labels.py # Script 2: Create label images
├── make_pdf.py # Script 3: Combine labels into PDF
├── monofonto rg.otf # Font used for label text
└── README.md


---

## Requirements

- Python 3.9+
- Internet connection (for barcode downloads)

### Python dependencies

```
pip install pandas requests pillow
```
### Input CSV Format
Your items.csv must contain the following columns:

### Column Name	
```Description, Barcode Number, Barcode value (numeric or text), Item Name, Name printed on the label```

#### Example:

```Barcode Number,Item Name```

```12345678,Widget A```

```98765432,Widget B```

## Script Overview
### 1️⃣ Download Barcode Images
File: download_barcodes.py

Reads items.csv

Downloads Code128 barcode images from barcodeapi.org

Saves images as PNGs in barcode_images/

Filenames are based on sanitized item names

Run:

`python download_barcodes.py`

### 2️⃣ Create Label Images
File: create_labels.py

Creates 50mm × 25mm labels at 300 DPI

Layout:

Top 2/3: barcode image

Bottom 1/3: item name (auto-scaled to fit)

Outputs black & white label PNGs to labels/

Font:

Uses monofonto rg.otf (must exist in project root)

Run:

`python create_labels.py`

### 3️⃣ Combine Labels into a PDF
File: make_pdf.py

Reads all PNG files from labels/

Combines them into a single multi-page PDF

Outputs labels.pdf

Run:

`python generate_pdf.py`


## Label Specifications
Size: 50mm × 25mm (but can be changed in script)

Resolution: 300 DPI

Color mode: Black & White (1-bit)

Optimized for: Thermal / label printers

## Notes & Tips
Item names are auto-scaled horizontally to prevent overflow

Missing barcodes or images are skipped with warnings

Filenames are sanitized to avoid OS issues

Barcode values are formatted to 2 decimal places when numeric

## Typical Workflow
`python download_barcodes.py`

`python create_labels.py`

`python make_pdf.py`

After this, labels.pdf is ready to print. 🏷️