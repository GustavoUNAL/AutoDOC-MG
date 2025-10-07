# AutoDOC-MG

## Project Overview
This project contains comprehensive analysis and optimization tools for relay coordination in power systems using genetic algorithms.

## Directory Structure
- `analysis/` - Jupyter notebooks for data analysis
  - `notebooks/` - Analysis notebooks for different scenarios
  - `reports/` - Generated analysis reports
- `data/` - Raw and processed data files
  - `raw/` - Original relay coordination data
  - `processed/` - Optimized relay settings and results
- `results/` - Generated reports, plots, and analysis results
  - `figures/` - Visualization plots (PNG format)
  - `tables/` - Data tables and summaries (CSV format)
  - `reports/` - Detailed analysis reports (TXT format)
- `scripts/` - Python scripts for automation and analysis
- `documentation/` - Project documentation and summaries

## Key Features
- **Genetic Algorithm Optimization**: Optimizes relay settings for all 68 scenarios
- **Comprehensive Analysis**: Before/after optimization comparison
- **Scenario-Specific Analysis**: Detailed analysis of problematic and best-performing scenarios
- **Automated Reporting**: Generates reports, visualizations, and summaries
- **Root Cause Analysis**: Identifies and analyzes optimization issues

## Setup
1. Clone the repository
2. Install required Python packages: `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`
3. Run the analysis notebooks or scripts

## Usage

### Quick Start
```bash
# Optimize all 68 scenarios
python scripts/optimize_all_scenarios.py

# Generate comprehensive report
python scripts/generate_comprehensive_report.py

# Analyze problematic scenario
python scripts/analyze_problematic_scenario.py
```

### Notebooks
- `analysis/notebooks/tmt_analysis_all_scenarios_comprehensive.ipynb` - Complete analysis of all scenarios
- `analysis/notebooks/tmt_optimization_ga.ipynb` - Genetic algorithm optimization
- `analysis/notebooks/scenario_2_problematic_analysis.ipynb` - Analysis of worst-performing scenario
- `analysis/notebooks/scenario_14_best_performance_analysis.ipynb` - Analysis of best-performing scenario

### Documentation
- `documentation/EXECUTIVE_SUMMARY_68_SCENARIOS.md` - Executive summary of optimization results
- `documentation/SCENARIO_2_PROBLEMATIC_ANALYSIS.md` - Detailed analysis of problematic scenario

## Results Summary
- **68 scenarios** successfully optimized using genetic algorithm
- **Average TMT improvement**: +15.348 seconds per scenario
- **Best performing scenario**: scenario_14 (+41.336s improvement)
- **Coordination improvement**: +85.1% average across all scenarios

## Environment
- Python 3.10+
- Required packages: `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `scipy`

## Collaboration
- Paths are auto-detected via portable `ProjectConfig` so the notebooks work across systems
- All outputs are in English and PNG format for international collaboration