from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from config import OUTPUT_GRAPHS, OUTPUT_CSV


FOCUS_ORDER = ["BF", "NF1", "NF2", "NF3", "NF4"]
FOCUS_LABELS = {
    "BF": "Broad Focus",
    "NF1": "Narrow Focus 1",
    "NF2": "Narrow Focus 2",
    "NF3": "Narrow Focus 3",
    "NF4": "Narrow Focus 4",
}


def focus_title(focus: str) -> str:
    return FOCUS_LABELS.get(focus, focus)


def save_fig(filename: str) -> None:
    OUTPUT_GRAPHS.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_GRAPHS / filename
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Created {out_file}")


def plot_f0() -> int:
    f0_path = OUTPUT_CSV / "F0_cleaned.csv"
    if not f0_path.exists():
        print(f"Skipping F0: missing {f0_path}")
        return 1

    df = pd.read_csv(f0_path)
    df["point"] = pd.to_numeric(df["point"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["list"] = pd.to_numeric(df["list"], errors="coerce")
    df = df.dropna(subset=["focus", "point", "value", "list"]).copy()
    df["point"] = df["point"].astype(int)
    df["list"] = df["list"].astype(int)

    graph_number = 1
    for focus in FOCUS_ORDER:
        focus_df = df[df["focus"] == focus].copy()
        if focus_df.empty:
            continue

        plt.figure(figsize=(8, 5))
        for list_id in sorted(focus_df["list"].unique()):
            subset = focus_df[focus_df["list"] == list_id].sort_values("point")
            plt.plot(subset["point"], subset["value"], marker="o", label=f"List {list_id}")

        plt.title(focus_title(focus))
        plt.xlabel("Point ID")
        plt.ylabel("f0 [Hz]")
        plt.xticks(range(1, 11))
        plt.xlim(0.5, 10.5)
        plt.ylim(100, 375)
        plt.grid(True, linestyle="--", alpha=0.35)
        plt.legend()

        suffix = focus_title(focus).lower().replace(" ", "_")
        save_fig(f"{graph_number:02d}_f0_{suffix}.png")
        graph_number += 1

    return graph_number


def plot_intensity(start_graph_number: int) -> None:
    intensity_path = OUTPUT_CSV / "Intensity_cleaned.csv"
    if not intensity_path.exists():
        print(f"Skipping Intensity: missing {intensity_path}")
        return

    df = pd.read_csv(intensity_path)
    df["point"] = pd.to_numeric(df["point"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["list"] = pd.to_numeric(df["list"], errors="coerce")
    df = df.dropna(subset=["focus", "point", "value", "list"]).copy()
    df["point"] = df["point"].astype(int)
    df["list"] = df["list"].astype(int)

    graph_number = start_graph_number
    for focus in FOCUS_ORDER:
        focus_df = df[df["focus"] == focus].copy()
        if focus_df.empty:
            continue

        plt.figure(figsize=(8, 5))
        for list_id in [1, 2, 3]:
            subset = focus_df[focus_df["list"] == list_id].copy()

            if subset.empty:
                # Keep legend entry even when a list has no data in this focus
                plt.plot([], [], marker="o", label=f"List {list_id}")
                continue

            # If multiple rows share the same point, collapse to one value per point
            subset = (
                subset.groupby("point", as_index=False)["value"]
                .mean()
                .sort_values("point")
            )

            plt.plot(subset["point"], subset["value"], marker="o", label=f"List {list_id}")

        plt.title(focus_title(focus))
        plt.xlabel("Point ID")
        plt.ylabel("Intensity [dB]")
        plt.xticks([11, 12, 13, 14])
        plt.xlim(10.5, 14.5)
        plt.ylim(78,88)
        plt.grid(True, linestyle="--", alpha=0.35)
        plt.legend()

        suffix = focus_title(focus).lower().replace(" ", "_")
        save_fig(f"{graph_number:02d}_intensity_{suffix}.png")
        graph_number += 1


def main() -> None:
    next_number = plot_f0()
    plot_intensity(next_number)


if __name__ == "__main__":
    main()