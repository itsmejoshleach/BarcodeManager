import os
from PIL import Image

# ——— CONFIG ———
LABEL_DIR = "labels"        # Folder with label images
OUTPUT_PDF = "labels.pdf"   # Output PDF filename

def main():
    # Get all PNG files in the labels folder
    images = [
        os.path.join(LABEL_DIR, f)
        for f in sorted(os.listdir(LABEL_DIR))
        if f.lower().endswith(".png")
    ]

    if not images:
        print("❌ No label images found in folder.")
        return

    pil_images = []
    for img_path in images:
        img = Image.open(img_path).convert("RGB")  # PDF needs RGB
        pil_images.append(img)

    # Save as PDF
    first_image = pil_images[0]
    rest_images = pil_images[1:]
    first_image.save(
        OUTPUT_PDF,
        save_all=True,
        append_images=rest_images
    )

    print(f"✅ PDF created: {OUTPUT_PDF}")

if __name__ == "__main__":
    main()
