from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import csv
from datetime import datetime

app = Flask(__name__)

# Path to your breeds CSV
CSV_PATH = os.path.join("data", "dog_breeds_groups.csv")

# Load data once
df = pd.read_csv(CSV_PATH)

# All breeds (for Best in Show dropdown)
all_breeds = df["breed"].tolist()

# Group -> list of breeds in that group
breeds_by_group = (
    df.groupby("group")["breed"]
      .apply(list)
      .to_dict()
)

# Make safe field names for HTML form (no spaces)
# Example: "Herding" -> "herding", "Non-Sporting" -> "non_sporting"
group_keys = []
for group_name in breeds_by_group.keys():
    key = group_name.lower().replace(" ", "_").replace("-", "_")
    group_keys.append((key, group_name))  # (form_field_name, display_name)


RESPONSES_PATH = os.path.join("data", "responses.csv")

def save_response(form_data):
    row = {"timestamp": datetime.now().isoformat(timespec="seconds")}

    # Add person name
    row["Name"] = form_data.get("person_name", "")

    # Add group picks
    for key, group_name in group_keys:
        row[group_name] = form_data.get(key, "")

    # Add Best in Show
    row["Best in Show"] = form_data.get("best_in_show", "")

    file_exists = os.path.exists(RESPONSES_PATH)
    fieldnames = ["timestamp", "Name"] + [g for _, g in group_keys] + ["Best in Show"]

    with open(RESPONSES_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Collect submitted data
        form_data = request.form.to_dict()
        save_response(form_data)
        
        # Redirect to results page instead of thank you
        return redirect(url_for("results"))

    # GET: show form
    return render_template(
        "index.html",
        group_keys=group_keys,
        breeds_by_group=breeds_by_group,
        all_breeds=all_breeds,
    )


@app.route("/results")
def results():
    if not os.path.exists(RESPONSES_PATH):
        # No responses yet
        return render_template("results.html", columns=[], rows=[])

    df_responses = pd.read_csv(RESPONSES_PATH)
    columns = df_responses.columns.tolist()
    rows = df_responses.to_dict(orient="records")

    return render_template("results.html", columns=columns, rows=rows)

if __name__ == "__main__":
    app.run(debug=True)