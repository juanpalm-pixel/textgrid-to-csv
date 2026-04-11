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

LIST_COLORS = {
    1: "#1f77b4",  # blue
    2: "#ff7f0e",  # orange
    3: "#2ca02c",  # green
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
            plt.plot(subset["point"], subset["value"], marker="o", label=f"List {list_id}", color=LIST_COLORS.get(list_id))

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


def plot_intensity(start_graph_number: int) -> int:
    intensity_path = OUTPUT_CSV / "Intensity_cleaned.csv"
    if not intensity_path.exists():
        print(f"Skipping Intensity: missing {intensity_path}")
        return start_graph_number

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
                plt.plot([], [], marker="o", label=f"List {list_id}", color=LIST_COLORS.get(list_id))
                continue

            # If multiple rows share the same point, collapse to one value per point
            subset = (
                subset.groupby("point", as_index=False)["value"]
                .mean()
                .sort_values("point")
            )

            plt.plot(subset["point"], subset["value"], marker="o", label=f"List {list_id}", color=LIST_COLORS.get(list_id))

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
    return graph_number

def plot_list_boundary_horizontal(graph_number: int) -> int:
    path = OUTPUT_CSV / "List Boundary_cleaned.csv"
    if not path.exists():
        print(f"Skipping List Boundary: missing {path}")
        return graph_number

    df = pd.read_csv(path)
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    df = df.dropna(subset=["name", "duration"]).copy()
    if df.empty:
        return graph_number

    y_labels = df["name"].astype(str).str.strip().tolist()
    x_vals = df["duration"].tolist()

    # Build one color per bar from "List <id>" in the label
    label_series = pd.Series(y_labels)
    list_id_series = pd.to_numeric(
        label_series.str.extract(r"(?i)list\s*(\d+)")[0],
        errors="coerce",
    )

    bar_colors = [
        LIST_COLORS.get(int(list_id), "#7f7f7f") if pd.notna(list_id) else "#7f7f7f"
        for list_id in list_id_series
    ]

    plt.barh(y_labels, x_vals, color=bar_colors)    
    plt.gca().invert_yaxis()
    plt.title("List Boundary")
    plt.xlabel("Duration (ms)")
    plt.ylabel("Segment")
    plt.grid(True, axis="x", linestyle="--", alpha=0.35)

    save_fig(f"{graph_number:02d}_list_boundary_horizontal.png")
    return graph_number + 1


def plot_stacked_duration_horizontal(
    csv_name: str,
    dataset_key: str,
    normalize: bool,
    graph_number: int,
) -> int:
    path = OUTPUT_CSV / csv_name
    if not path.exists():
        print(f"Skipping {dataset_key}: missing {path}")
        return graph_number

    df = pd.read_csv(path)
    df["start"] = pd.to_numeric(df["start"], errors="coerce")
    df["stop"] = pd.to_numeric(df["stop"], errors="coerce")

    if "duration" in df.columns:
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    else:
        df["duration"] = df["stop"] - df["start"]

    df["list"] = pd.to_numeric(df["list"], errors="coerce")
    df = df.dropna(subset=["focus", "list", "name", "duration", "start"]).copy()
    df["list"] = df["list"].astype(int)

    for focus in FOCUS_ORDER:
        focus_df = df[df["focus"] == focus].copy()
        if focus_df.empty:
            continue

        focus_df = focus_df.sort_values(["list", "start"])
        lists_here = sorted(focus_df["list"].unique())

        plt.figure(figsize=(10, 5))

        for row_index, list_id in enumerate(lists_here):
            row_df = focus_df[focus_df["list"] == list_id].copy()
            total = row_df["duration"].sum()
            left = 0.0

            for _, r in row_df.iterrows():
                dur = float(r["duration"])
                width = (dur / total * 100.0) if (normalize and total > 0) else dur

                plt.barh(
                    y=f"List {list_id}",
                    width=width,
                    left=left,
                    color=LIST_COLORS.get(list_id),
                    edgecolor="white",
                    linewidth=1.0,
                    alpha=0.9,
                )

                if width > (3.0 if normalize else 0.08):
                    plt.text(
                        left + width / 2.0,
                        row_index,
                        f"{int(dur)} ms",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="black",
                    )

                left += width

        plt.title(f"{focus_title(focus)}")
        plt.xlabel("Percent of Total Duration (%)" if normalize else "Duration (ms)")
        plt.ylabel("List")
        plt.grid(True, axis="x", linestyle="--", alpha=0.35)
        plt.gca().invert_yaxis()

        if normalize:
            plt.xlim(0, 100)

        suffix = focus_title(focus).lower().replace(" ", "_")
        save_fig(f"{graph_number:02d}_{dataset_key}_{suffix}_stacked.png")
        graph_number += 1

    return graph_number

def main() -> None:
    graph_number = plot_f0()
    graph_number = plot_intensity(graph_number)
    graph_number = plot_list_boundary_horizontal(graph_number)
    graph_number = plot_stacked_duration_horizontal("PW_cleaned.csv", "pw", True, graph_number)
    graph_number = plot_stacked_duration_horizontal("Syllable_cleaned.csv", "syllable", True, graph_number)

if __name__ == "__main__":
    main()