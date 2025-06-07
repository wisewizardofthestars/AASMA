## Overview
This project runs repeated tournaments of the Iterared prisoner's dilemma with randomly generated strategies, saves the results, and visualizes the data. It is designed to explore how different strategies perform against each other in a repeated game setting.

## Requirements
- Python 3.8+
- `numpy`
- `statsmodels`
- `pandas`
- `axelrod`
- `matplotlib`
- `seaborn`
- `joblib`
- `scikit-learn`

## How to Run
For random payoffs use:
```bash
python3 main.py --runs 10 --filename csv/
```

For fixed payoffs use:
```bash
python3 fixed_payoffs.py
```

## Visualize results
You can use the provided Jupyter notebook to visualize the results of the tournaments with random payoffs:
```bash
visualize_results.ipynb
```
You can use the provided Jupyter notebook to visualize the results of the tournaments with fixed payoffs:
```bash
fixed_payoffs/visualize_results_fixed_payoffs.py
```
