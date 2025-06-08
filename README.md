## Overview
This project runs repeated tournaments of the Iterated Prisoner's Dilemma with randomly generated strategies, saves the results, and visualizes the data. It is designed to explore how different strategies perform against each other in a repeated game setting, supporting advanced statistical analysis and visualizations.

## Requirements
- Python 3.8+
- numpy
- statsmodels
- pandas
- axelrod
- matplotlib
- seaborn
- joblib
- scikit-learn
- ffmpeg (system executable, for animation saving)

## Installation
1. Install Python dependencies:
   ```bash
   pip install numpy statsmodels pandas axelrod matplotlib seaborn joblib scikit-learn
   ```
2. Install ffmpeg (required for saving animations as .mp4):
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html) (choose a Windows build if on Windows, or install with apt ffmpeg in Ubuntu).
   - Extract and add the `bin` folder to your system PATH.
   - Verify installation by running `ffmpeg -version` in a new terminal.

## How to Run
Run with random payoffs (10 runs, results in `csv/`):
```bash
python main.py --runs 10 
```


## Visualize Results
Use the provided Jupyter notebook to visualize tournament results:
```bash
jupyter notebook visualize_results.ipynb
```
Or run the Python scripts for advanced analysis and plots.

## Notes
- All result CSVs and plots will be saved in the specified output directory (e.g., `csv/`).
- For animation saving, ensure ffmpeg is installed and accessible in your PATH.
