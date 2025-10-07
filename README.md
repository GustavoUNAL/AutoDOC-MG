# AutoDOC-MG - TMT Analysis

This repository contains notebooks and utilities to perform Total Miscoordination Time (TMT) analysis for relay coordination studies.

## Notebooks
- `analysis/notebooks/tmt_analysis_all_scenarios.ipynb`: Full analysis across all scenarios. Generates CSV, JSON, TXT reports, and PNG plots (no HTML).
- `analysis/notebooks/tmt_analysis_scenario_1.ipynb`: Focused analysis for `scenario_1` only. Includes per-pair visuals and inline charts.

## Data
- Input JSON: `data/raw/automation_results.json`

## Results
- Tables (CSV/JSON): `results/tables/`
- Reports (TXT): `results/reports/`
- Plots (PNG): `results/plots/tmt_analysis/`

## Running
1. Open the desired notebook in Jupyter (or VS Code/Cursor) and run all cells.
2. Ensure `automation_results.json` exists under `data/raw/`.
3. PNG export uses Plotly's image engine. If PNG export fails due to Chrome/Kaleido, charts still render inline in the notebook. To enable PNG export:
   - Install Kaleido and Chrome: `pip install kaleido` then run `plotly_get_chrome`.

## Environment
- Python 3.10+
- Required packages: `pandas`, `numpy`, `plotly`, `scipy`

## Collaboration
- Paths are auto-detected via portable `ProjectConfig` so the notebooks work across systems.

