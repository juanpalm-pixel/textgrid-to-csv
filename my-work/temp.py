import textgrid
from config import INPUT_FILE, OUTPUT_DIR

tgrid = textgrid.read_textgrid(str(INPUT_FILE), fileEncoding="utf-16")
print(tgrid[:3])

ordered_tiers = []
for e in tgrid:
    if e.tier not in ordered_tiers:
        ordered_tiers.append(e.tier)

for i, tier_name in enumerate(ordered_tiers[:4], start=1):
    tier_rows = [e for e in tgrid if e.tier == tier_name]
    out_file = OUTPUT_DIR / f"tier_{i}_{tier_name}.csv"
    textgrid.write_csv(tier_rows, str(out_file), meta=False)