from pathlib import Path
import csv
import re

# Add as many files as you want here
FILES1 = [
    Path("output/csv/Intensity.csv"),
    Path("output/csv/F0.csv"),
]

for path in FILES1:
    rows_out = []
    stem = path.stem.lower()

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

            time_value = f"{float(row.get('start', 0.0)):.3f}"

            if value:
                if stem == "f0":
                    value = f"{float(value):.0f}"
                elif stem == "intensity":
                    value = f"{float(value):.1f}"
            
            rows_out.append(
                {
                    "time": time_value,
                    "point": point,
                    "value": value,
                }
            )

        # Add extra columns by file type
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
            list_pattern = [1] * 20 + [2] * 20 + [3] * 20

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

# Keep this separate so FILES1 behavior stays unchanged
FILES2 = [
    Path("output/csv/PW.csv"),
    Path("output/csv/Syllable.csv"),  
]

PW_ALLOWED = {"Wysłali", "dziecko", "na dwór", "bez czapki", "WYSŁALI", "DZIECKO", "NA DWÓR", "bez CZAPKI","sła", "dziec", "na", "czap"}

for path in FILES2:
    rows_out = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        if "name" not in fieldnames:
            raise ValueError(f"'name' column not found in {path}")

        for row in reader:
            # normalize whitespace so values like "Wysłali " still match
            label = " ".join((row.get("name") or "").split())
            if label in PW_ALLOWED:
                start_val = float(row["start"])
                stop_val = float(row["stop"])
                duration_val = (stop_val - start_val) * 1000  # convert to ms

                row["name"] = label
                row["start"] = f"{start_val:.3f}"
                row["stop"] = f"{stop_val:.3f}"
                row["duration"] = f"{duration_val:.1f}"  # ms typically needs fewer decimals
                rows_out.append(row)

    # Add patterns after PW/Syllable is cleaned
    list_pattern = [1] * 20 + [2] * 20 + [3] * 20
    focus_pattern = ["BF"] * 4 + ["NF1"] * 4 + ["NF2"] * 4 + ["NF3"] * 4 + ["NF4"] * 4

    for i, r in enumerate(rows_out):
        r["list"] = list_pattern[i % len(list_pattern)]
        r["focus"] = focus_pattern[i % len(focus_pattern)]

    out_path = path.with_name(path.stem + "_cleaned.csv")
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["start", "stop", "duration", "name", "tier", "list", "focus"]
        )
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Done: {path} -> {out_path}")

FILES3 = [Path("output/csv/List Boundary.csv")]

for input_path in FILES3:
    rows_out = []

    with input_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if "name" not in (reader.fieldnames or []):
            raise ValueError(f"'name' column not found in {input_path}")

        for row in reader:
            label = (row.get("name") or "").strip()

            # Delete rows where name matches [word]
            if re.fullmatch(r"\[\w*\]", label):
                continue

             # Remove List 1
            if re.fullmatch(r"(?i)list\s*1", label):
                continue

            start_val = float(row["start"])
            stop_val = float(row["stop"])
            duration_val = (stop_val - start_val) * 1000  # convert to ms

            row["name"] = label
            row["start"] = f"{start_val:.3f}"
            row["stop"] = f"{stop_val:.3f}"
            row["duration"] = f"{duration_val:.1f}"  # ms typically needs fewer decimals
            rows_out.append(row)
    # Rename remaining rows to List 1, List 2, ...
    for i, row in enumerate(rows_out, start=1):
        row["name"] = f"List {i}"

    output_path = input_path.with_name(f"{input_path.stem}_cleaned.csv")
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["start", "stop", "duration", "name", "tier"]
        )
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Done: {input_path} -> {output_path}")