from flask import Flask, render_template, request, send_from_directory, flash
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Directories
BARCODE_DIR = os.path.join("static", "barcode_images")
LABEL_DIR = os.path.join("static", "labels")

# Load CSV
CSV_PATH = "items.csv"
df = pd.read_csv(CSV_PATH).fillna("")

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("search", "").strip()

        if not query:
            flash("Please enter a name, description, or barcode.", "warning")
        else:
            # Try formatting barcode to 2 decimal places
            try:
                barcode_query = f"{float(query):.2f}"
            except ValueError:
                barcode_query = None

            # Perform search
            matches = df[
                (df["Item Name"].str.contains(query, case=False)) |
                (df["Item Description / Alternate Names"].str.contains(query, case=False)) |
                ((df["Barcode Number"].astype(str) == barcode_query) if barcode_query else False)
            ]

            if matches.empty:
                flash("No matching items found.", "danger")
            else:
                for _, row in matches.iterrows():
                    item_name = row["Item Name"]
                    barcode_number = f"{float(row['Barcode Number']):.2f}"

                    barcode_file = f"{item_name}.png"
                    label_file = f"{item_name}_label.png"

                    results.append({
                        "name": item_name,
                        "description": row["Item Description / Alternate Names"],
                        "barcode": barcode_number,
                        "barcode_image": barcode_file if os.path.exists(os.path.join(BARCODE_DIR, barcode_file)) else None,
                        "label_image": label_file if os.path.exists(os.path.join(LABEL_DIR, label_file)) else None
                    })

    return render_template("index.html", query=query, results=results)

@app.route("/barcode_images/<filename>")
def barcode_image(filename):
    return send_from_directory(BARCODE_DIR, filename)

@app.route("/labels/<filename>")
def label_image(filename):
    return send_from_directory(LABEL_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)   
