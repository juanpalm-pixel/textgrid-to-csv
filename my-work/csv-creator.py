import csv
import re
import textgrid
from config import INPUT_FILE, OUTPUT_CSV

tgrid = textgrid.read_textgrid(str(INPUT_FILE), fileEncoding="utf-16")
print(tgrid[:3])

OUTPUT_CSV.mkdir(parents=True, exist_ok=True)  # ensure output/csv exists

ordered_tiers = []
for e in tgrid:
    if e.tier not in ordered_tiers:
        ordered_tiers.append(e.tier)


for tier_name in ordered_tiers[:7]:
    tier_rows = [e for e in tgrid if e.tier == tier_name]
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", tier_name)
    out_file = OUTPUT_CSV / f"{safe_name}.csv"

    with out_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["start", "stop", "name", "tier"])
        for e in tier_rows:
            writer.writerow([e.start, e.stop, e.name, e.tier])