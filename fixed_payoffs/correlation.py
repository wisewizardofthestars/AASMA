"""A script for running the correlation analysis on the marged data set."""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

font = {"size": 10, "weight": "bold"}
matplotlib.rc("font", **font)

# Use local plot.py for feature label mapping if available
try:
    import plot
    features_labels = plot.features_labels
except Exception:
    features_labels = {
        "CC_to_C_rate": "$CC$ to $C$ rate",
        "CD_to_C_rate": "$CD$ to $C$ rate",
        "DC_to_C_rate": "$DC$ to $C$ rate",
        "DD_to_C_rate": "$DD$ to $C$ rate",
        "SSE": "SSE",
        "Makes_use_of_game": "Make use of game",
        "Makes_use_of_length": "Make use of length",
        "Stochastic": "stochastic",
        "Cooperation_rating": r"$C_r$",
        "Cooperation_rating_max": r"$C_{max}$",
        "Cooperation_rating_min": r"$C_{min}$",
        "Cooperation_rating_median": r"$C_{median}$",
        "Cooperation_rating_mean": r"$C_{mean}$",
        "Cooperation_rating_comp_to_max": r"$C_r$ / $C_{max}$ ",
        "Cooperation_rating_comp_to_min": r"$C_r$ / $C_{min}$",
        "Cooperation_rating_comp_to_median": r"$C_r$ / $C_{median}$",
        "Cooperation_rating_comp_to_mean": r"$C_r$ / $C_{mean}$",
        "size": r"$N$",
        "turns": r"$n$",
        "probend": r"$p_e$",
        "noise": r"$p_n$",
        "memory_usage": "memory usage",
        "repetitions": r"$k$",
        "Normalized_Rank": r"$r$",
        "Median_score": "median score",
    }

# Use merged processed fixed-payoff data
input_path = os.path.join(os.path.dirname(__file__), '../csv/fixed_payoff_merged_processed.csv')
output_dir = os.path.join(os.path.dirname(__file__), '../paper')
os.makedirs(output_dir, exist_ok=True)

clustering_on = ["Normalized_rank", "Median_score"]
features = [
    "CC_to_C_rate", "CD_to_C_rate", "DC_to_C_rate", "DD_to_C_rate", "SSE",
    "Makes_use_of_game", "Makes_use_of_length", "Stochastic", "Cooperation_rating",
    "Cooperation_rating_max", "Cooperation_rating_min", "Cooperation_rating_median",
    "Cooperation_rating_mean", "Cooperation_rating_comp_to_max", "Cooperation_rating_comp_to_min",
    "Cooperation_rating_comp_to_median", "Cooperation_rating_comp_to_mean", "size", "turns",
    "probend", "noise", "memory_usage", "repetitions"
]

sort = [
    "$CC$ to $C$ rate", "$CD$ to $C$ rate", "$C_r$", "$C_r$ / $C_{max}$ ", "$C_r$ / $C_{mean}$",
    "$C_r$ / $C_{median}$", "$C_{max}$", "$C_{mean}$", "$C_{median}$", "$C_{min}$", "$C_{min}$ / $C_r$",
    "$DC$ to $C$ rate", "$DD$ to $C$ rate", "$N$", "$k$", "$n$", "$p_e$", "$p_n$", "Make use of game",
    "Make use of length", "SSE", "memory usage", "stochastic"
]

df = pd.read_csv(input_path)

corr_data = df[[f for f in features if f in df.columns] + [c for c in clustering_on if c in df.columns]].corr()
table = corr_data[[c for c in clustering_on if c in corr_data.columns]].iloc[:-len(clustering_on)].round(3)
table.index = [features_labels.get(index, index) for index in table.index]

with open(os.path.join(output_dir, "correlation_table_fixedpayoff.tex"), "w") as textfile:
    textfile.write(
        table.reindex([s for s in sort if s in table.index])
        .to_latex()
        .replace("$\\$", "$")
        .replace("\\_", "_")
        .replace("\\{", "{")
        .replace("\\}", "}")
    )

corr_data = df[[f for f in features if f in df.columns] + [c for c in clustering_on if c in df.columns]]
corrmat = corr_data.corr()
top_corr_features = corrmat.index

data = corr_data[top_corr_features].corr().round(3)
data.columns = [features_labels.get(feature, feature) for feature in data.columns]
data.index = [features_labels.get(feature, feature) for feature in corr_data.corr().index]

plt.figure(figsize=(20, 15))
sns.heatmap(data, annot=True, cmap="viridis")
plt.savefig(os.path.join(output_dir, "fixedpayoff_correlation_plot.pdf"), bbox_inches="tight")