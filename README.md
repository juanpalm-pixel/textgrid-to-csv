# textgrid-to-csv

This repo takes a Praat TextGrid file, turns it into CSVs, cleans key tiers, and makes graphs.

## How to run it

1. Put your TextGrid in the `input` folder.
2. Run:

```bat
setup.bat
```

This installs/checks the Python dependencies.

3. Then run:

```bat
complete.bat
```

This runs the full pipeline (create CSV -> clean CSV -> make graphs).

## Where output is

- `output/csv`
  - Raw tier exports and cleaned files.
  - Files ending in `_cleaned.csv` are the processed versions used for plotting.

- `output/graphs`
  - Final PNG plots.
  - Numbered files are just the graph order.

## What the output means

- CSV files = the data tables extracted from TextGrid tiers.
- Cleaned CSV files = normalized values with extra analysis columns (like list/focus) where needed.
- Graph PNGs = visual summaries of F0, Intensity, List Boundary, PW, and Syllable timing patterns.
