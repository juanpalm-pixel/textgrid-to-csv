from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
GRAPH_DIR = OUTPUT_DIR / "graphs"


def focus_sort_key(focus: str) -> tuple[int, int | str]:
	if focus == "BF":
		return (0, 0)
	if focus.startswith("NF"):
		suffix = focus[2:]
		return (1, int(suffix) if suffix.isdigit() else suffix)
	return (2, focus)


def save_plot(base_name: str, suffix: str, graph_number: int) -> Path:
	out_file = GRAPH_DIR / f"{graph_number:02d}_{base_name}_{suffix}.png"
	plt.tight_layout()
	plt.savefig(out_file, dpi=150)
	plt.close()
	print(f"Created {out_file}")
	return out_file


def plot_point_value_lines(frame: pd.DataFrame, base_name: str, graph_number: int) -> int:
	frame = frame.copy()
	frame["point"] = pd.to_numeric(frame["point"], errors="coerce")
	frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
	frame["list"] = pd.to_numeric(frame["list"], errors="coerce")
	frame = frame.dropna(subset=["focus", "point", "value", "list"]).copy()
	frame["list"] = frame["list"].astype(int)

	focus_values = sorted(frame["focus"].astype(str).unique(), key=focus_sort_key)
	list_values = sorted(frame["list"].unique())

	for focus in focus_values:
		focus_data = frame[frame["focus"] == focus]
		if focus_data.empty:
			continue

		plt.figure(figsize=(8, 5))
		for list_id in list_values:
			subset = focus_data[focus_data["list"] == list_id].sort_values("point")
			if subset.empty:
				continue
			plt.plot(subset["point"], subset["value"], marker="o", label=f"list {list_id}")

		plt.title(f"{base_name.upper()} - {focus}")
		plt.xlabel("point")
		plt.ylabel("value")
		plt.grid(True, linestyle="--", alpha=0.35)
		plt.legend()
		save_plot(base_name, focus.lower(), graph_number)
		graph_number += 1

	return graph_number


def plot_duration_lines(frame: pd.DataFrame, base_name: str, graph_number: int) -> int:
	frame = frame.copy()
	frame["start"] = pd.to_numeric(frame["start"], errors="coerce")
	frame["stop"] = pd.to_numeric(frame["stop"], errors="coerce")
	frame["list"] = pd.to_numeric(frame["list"], errors="coerce")
	frame = frame.dropna(subset=["focus", "name", "start", "stop", "list"]).copy()
	frame["duration"] = frame["stop"] - frame["start"]
	frame["list"] = frame["list"].astype(int)

	focus_values = sorted(frame["focus"].astype(str).unique(), key=focus_sort_key)
	list_values = sorted(frame["list"].unique())

	for focus in focus_values:
		focus_data = frame[frame["focus"] == focus]
		if focus_data.empty:
			continue

		plt.figure(figsize=(9, 5))
		token_order = list(dict.fromkeys(focus_data["name"].astype(str)))

		for list_id in list_values:
			subset = focus_data[focus_data["list"] == list_id].copy()
			if subset.empty:
				continue

			subset["name"] = pd.Categorical(subset["name"], categories=token_order, ordered=True)
			subset = subset.sort_values("name")
			plt.plot(subset["name"], subset["duration"], marker="o", label=f"list {list_id}")

		plt.title(f"{base_name.upper()} - {focus}")
		plt.xlabel("token")
		plt.ylabel("duration (s)")
		plt.grid(True, axis="y", linestyle="--", alpha=0.35)
		plt.legend()
		save_plot(base_name, focus.lower(), graph_number)
		graph_number += 1

	return graph_number


def plot_boundary_bar(frame: pd.DataFrame, base_name: str, graph_number: int) -> int:
	frame = frame.copy()
	frame["duration"] = pd.to_numeric(frame["duration"], errors="coerce")
	frame = frame.dropna(subset=["name", "duration"]).copy()
	if frame.empty:
		return graph_number

	plt.figure(figsize=(8, 5))
	plt.bar(frame["name"].astype(str), frame["duration"], color="#4472C4")
	plt.title(f"{base_name.upper()} - Segment Durations")
	plt.xlabel("segment")
	plt.ylabel("duration (s)")
	plt.grid(True, axis="y", linestyle="--", alpha=0.35)
	save_plot(base_name, "durations", graph_number)
	return graph_number + 1


def main() -> None:
	GRAPH_DIR.mkdir(parents=True, exist_ok=True)

	cleaned_files = sorted(OUTPUT_DIR.glob("*_cleaned.csv"))
	if not cleaned_files:
		raise FileNotFoundError("No *_cleaned.csv files found in output directory")

	graph_number = 1
	for csv_path in cleaned_files:
		base_name = csv_path.stem.replace("_cleaned", "").replace(" ", "_").lower()
		frame = pd.read_csv(csv_path)
		columns = set(frame.columns)

		if {"point", "value", "list", "focus"}.issubset(columns):
			graph_number = plot_point_value_lines(frame, base_name, graph_number)
		elif {"start", "stop", "name", "list", "focus"}.issubset(columns):
			graph_number = plot_duration_lines(frame, base_name, graph_number)
		elif {"name", "duration"}.issubset(columns):
			graph_number = plot_boundary_bar(frame, base_name, graph_number)
		else:
			print(f"Skipping {csv_path.name}: unsupported schema")


if __name__ == "__main__":
	main()
