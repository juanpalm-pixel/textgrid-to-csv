from pathlib import Path
import csv
import re

# Add as many files as you want here
FILES = [
    Path("output/Intensity.csv"),
    Path("output/F0.csv"),
]

for path in FILES:
    rows_out = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = (row.get("name") or "").strip()

            # Split like "11.) 87.6" -> point="11.)", value="87.6"
            m = re.match(r"^(.*?\)\s*)\s*([-+]?\d*\.?\d+)$", raw)
            if m:
                point = m.group(1).strip()
                point = re.sub(r"\.\)$", "", point).strip()  # "11.)" -> "11"
                value = m.group(2).strip()
            else:
                point = raw
                point = re.sub(r"\.\)$", "", point).strip()
                value = ""
            
            rows_out.append(
                {
                    "time": row.get("start", ""),
                    "point": point,
                    "value": value,
                }
            )

        # Add extra columns by file type
        stem = path.stem.lower()

        if stem == "f0":
            # list: 1..3 each 50 (total cycle length 150)
            list_pattern = [1] * 50 + [2] * 50 + [3] * 50

            # focus: BF/NF1/NF2/NF3/NF4 each 10, repeated 3 times (length 150)
            focus_pattern = (
                (["BF"] * 10 + ["NF1"] * 10 + ["NF2"] * 10 + ["NF3"] * 10 + ["NF4"] * 10) * 3
            )

            for i, r in enumerate(rows_out):
                r["list"] = list_pattern[i % len(list_pattern)]
                r["focus"] = focus_pattern[i % len(focus_pattern)]

            fieldnames = ["time", "point", "value", "list", "focus"]

        elif stem == "intensity":
            # list: same as pattern1 in R (1..3 each 50), truncated to n rows
            list_pattern = [1] * 50 + [2] * 50 + [3] * 50

            # focus: BF/NF1/NF2/NF3/NF4 each 4 (cycle length 20), repeated to n rows
            focus_pattern = ["BF"] * 4 + ["NF1"] * 4 + ["NF2"] * 4 + ["NF3"] * 4 + ["NF4"] * 4

            for i, r in enumerate(rows_out):
                r["list"] = list_pattern[i % len(list_pattern)]
                r["focus"] = focus_pattern[i % len(focus_pattern)]

            fieldnames = ["time", "point", "value", "list", "focus"]

        else:
            fieldnames = ["time", "point", "value"]

    # Save to a new file so original stays untouched
    out_path = path.with_name(path.stem + "_cleaned.csv")
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Done: {path} -> {out_path}")