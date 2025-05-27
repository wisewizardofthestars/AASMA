import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# List of result files to visualize
types = ['standard', 'noisy', 'probabilistic', 'prob_noisy']
dfs = []

for t in types:
    filename = f"{t}_aggregated.csv"
    if not os.path.exists(filename):
        print(f"File {filename} not found, skipping.")
        continue
    df = pd.read_csv(filename)
    df['tournament_type'] = t
    dfs.append(df)
    # Plot average score per strategy (original barplot)
    if 'Name' in df.columns and 'Median_score' in df.columns:
        plt.figure(figsize=(12, 6))
        avg_scores = df.groupby('Name')['Median_score'].mean().sort_values(ascending=False)
        sns.barplot(x=avg_scores.index, y=avg_scores.values)
        plt.title(f"Average Median Score per Strategy - {t.capitalize()} Tournament")
        plt.ylabel("Average Median Score")
        plt.xlabel("Strategy")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(f"{t}_avg_scores.png")
        plt.close()
        print(f"Saved plot: {t}_avg_scores.png")
    else:
        print(f"'Name' or 'Median_score' column not found in {filename}, skipping plot.")

# Advanced analysis and comparison plots
if dfs:
    all_data = pd.concat(dfs, ignore_index=True)
    # Boxplot: Score distribution per strategy per tournament type
    if 'Name' in all_data.columns and 'Median_score' in all_data.columns and 'tournament_type' in all_data.columns:
        plt.figure(figsize=(16, 8))
        sns.boxplot(data=all_data, x='Name', y='Median_score', hue='tournament_type')
        plt.title("Median Score Distribution per Strategy Across Tournament Types")
        plt.ylabel("Median Score")
        plt.xlabel("Strategy")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig("score_distribution_boxplot.png")
        plt.close()
        print("Saved plot: score_distribution_boxplot.png")

        # Grouped barplot: Mean median score per strategy per tournament type
        mean_scores = all_data.groupby(['Name', 'tournament_type'])['Median_score'].mean().reset_index()
        plt.figure(figsize=(16, 8))
        sns.barplot(data=mean_scores, x='Name', y='Median_score', hue='tournament_type')
        plt.title("Mean Median Score per Strategy Across Tournament Types")
        plt.ylabel("Mean Median Score")
        plt.xlabel("Strategy")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig("mean_score_comparison.png")
        plt.close()
        print("Saved plot: mean_score_comparison.png")
    else:
        print("Required columns not found for advanced plots.")
