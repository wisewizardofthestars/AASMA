"""A script for running the regression analysis on the marged data set."""
import pandas as pd
import statsmodels.api as sm
import os

# Use local plot.py for feature label mapping if available
try:
    import fixed_payoffs.plot as plot
    features_labels = plot.features_labels
except Exception:
    features_labels = {
        "CC_to_C_rate": "$CC$ to $C$ rate",
        "CD_to_C_rate": "$CD$ to $C$ rate",
        "DC_to_C_rate": "$DC$ to $C$ rate",
        "SSE": "SSE",
        "Cooperation_rating_comp_to_min": "$C_r$ / $C_{min}$",
        "Cooperation_rating_comp_to_mean": "$C_r$ / $C_{mean}$",
    }

# Adapted for your processed merged data
input_path = os.path.join(os.path.dirname(__file__), 'csv', 'fixed_payoff_merged_processed.csv')
output_dir = os.path.join(os.path.dirname(__file__), '..', 'paper')
os.makedirs(output_dir, exist_ok=True)

# Features for regression
features = [
    "CC_to_C_rate",
    "CD_to_C_rate",
    "DC_to_C_rate",
    "SSE",
    "Cooperation_rating_comp_to_min",
    "Cooperation_rating_comp_to_mean",
]

# Load data
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Input file not found: {input_path}")
df = pd.read_csv(input_path)

xs = features.copy()
X = df[xs].values
y = df['Median_score'].values

X = sm.add_constant(X)
model = sm.OLS(y, X).fit()

table = model.summary2(xname=['constant'] + xs)
rs = table.tables[0][2][0] + table.tables[0][3][0]
table = table.tables[1][['Coef.', 'P>|t|']].round(5)
table.index = ['constant'] + [features_labels.get(index, index) for index in table.index[1:]]

with open(os.path.join(output_dir, 'regression_fixedpayoff_result_on_median_score.tex'), "w") as file:
    file.write(table.round(3).to_latex().replace('\\$', '$').replace('\\_', ('_')))

with open(os.path.join(output_dir, 'r_square_fixedpayoff_result_on_median_score.tex'), "w") as file:
    file.write(str(rs))