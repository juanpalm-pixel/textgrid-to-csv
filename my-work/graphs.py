from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
GRAPH_DIR = OUTPUT_DIR / "graphs"

DATASETS = [
	("f0", OUTPUT_DIR / "F0_cleaned.csv"),
	("intensity", OUTPUT_DIR / "Intensity_cleaned.csv"),
]

# Four graphs per dataset (BF, NF1, NF2, NF3) -> 8 graphs total.
FOCUS_ORDER = ["BF", "NF1", "NF2", "NF3"]

# Plot up to four list lines if present.
LIST_ORDER = [1, 2, 3, 4]


def create_graph(data: pd.DataFrame, dataset_name: str, focus: str, graph_number: int) -> None:
	plt.figure(figsize=(8, 5))

	for list_id in LIST_ORDER:
		subset = data[data["list"] == list_id].copy()
		if subset.empty:
			continue

		subset = subset.sort_values("point")
		plt.plot(subset["point"], subset["value"], marker="o", label=f"list {list_id}")

	plt.title(f"{dataset_name.upper()} - {focus}")
	plt.xlabel("point")
	plt.ylabel("value")
	plt.grid(True, linestyle="--", alpha=0.35)
	plt.legend()
	plt.tight_layout()

	out_file = GRAPH_DIR / f"{graph_number:02d}_{dataset_name}_{focus.lower()}.png"
	plt.savefig(out_file, dpi=150)
	plt.close()
	print(f"Created {out_file}")


def main() -> None:
	GRAPH_DIR.mkdir(parents=True, exist_ok=True)

	graph_number = 1
	for dataset_name, csv_path in DATASETS:
		if not csv_path.exists():
			raise FileNotFoundError(f"Missing file: {csv_path}")

		frame = pd.read_csv(csv_path)
		frame["point"] = pd.to_numeric(frame["point"], errors="coerce")
		frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
		frame["list"] = pd.to_numeric(frame["list"], errors="coerce")

		frame = frame.dropna(subset=["focus", "point", "value", "list"]).copy()
		frame["list"] = frame["list"].astype(int)

		for focus in FOCUS_ORDER:
			focus_data = frame[frame["focus"] == focus].copy()
			if focus_data.empty:
				print(f"Skipping {dataset_name} {focus}: no rows")
				continue

			create_graph(focus_data, dataset_name, focus, graph_number)
			graph_number += 1


if __name__ == "__main__":
	main()
