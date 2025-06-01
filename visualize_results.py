import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import scipy
import re

# List of result files to visualize
types = ['standard', 'noisy', 'probabilistic', 'prob_noisy']
dfs = []

def extract_base_name(name):
    # Remove anything after ':' or '(' or '[' (for meta strategies and parameterized names)
    return re.split(r'[:\(\[]', name)[0].strip()

for t in types:
    filename = os.path.join("csv", f"{t}_aggregated.csv")
    if not os.path.exists(filename):
        print(f"File {filename} not found, skipping.")
        continue
    df = pd.read_csv(filename)
    df['tournament_type'] = t
    df['BaseName'] = df['Name'].apply(extract_base_name)
    dfs.append(df)
    # Plot average score per strategy (original barplot)
    if 'BaseName' in df.columns and 'Median_score' in df.columns:
        plt.figure(figsize=(12, 6))
        # Group by BaseName only, averaging across all runs/conditions for this tournament type
        avg_scores = df.groupby('BaseName')['Median_score'].mean().sort_values(ascending=False)
        sns.barplot(x=avg_scores.index, y=avg_scores.values)
        plt.title(f"Average Median Score per Strategy - {t.capitalize()} Tournament")
        plt.ylabel("Average Median Score")
        plt.xlabel("Strategy")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(f"graphs/{t}_avg_scores.png")
        plt.close()
        print(f"Saved plot: graphs/{t}_avg_scores.png")
    else:
        print(f"'BaseName' or 'Median_score' column not found in {filename}, skipping plot.")

# Advanced analysis and comparison plots
if dfs:
    all_data = pd.concat(dfs, ignore_index=True)
    all_data['BaseName'] = all_data['Name'].apply(extract_base_name)
    # Boxplot: Score distribution per strategy per tournament type
    if 'BaseName' in all_data.columns and 'Median_score' in all_data.columns and 'tournament_type' in all_data.columns:
        plt.figure(figsize=(16, 8))
        # Group by BaseName and tournament_type, not by all columns
        sns.boxplot(data=all_data, x='BaseName', y='Median_score', hue='tournament_type')
        plt.title("Median Score Distribution per Strategy Across Tournament Types")
        plt.ylabel("Median Score")
        plt.xlabel("Strategy")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig("graphs/score_distribution_boxplot.png")
        plt.close()
        print("Saved plot: graphs/score_distribution_boxplot.png")

        # Grouped barplot: Mean median score per strategy per tournament type
        mean_scores = all_data.groupby(['BaseName', 'tournament_type'])['Median_score'].mean().reset_index()
        plt.figure(figsize=(16, 8))
        sns.barplot(data=mean_scores, x='BaseName', y='Median_score', hue='tournament_type')
        plt.title("Mean Median Score per Strategy Across Tournament Types")
        plt.ylabel("Mean Median Score")
        plt.xlabel("Strategy")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig("graphs/mean_score_comparison.png")
        plt.close()
        print("Saved plot: graphs/mean_score_comparison.png")
    else:
        print("Required columns not found for advanced plots")

        # Correlation heatmap of numeric variables
        numeric_cols = ['Median_score', 'Cooperation_rating', 'noise', 'prob_end', 'repetitions', 'turns', 'n_strategies']
        corr = all_data[numeric_cols].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title('Correlation Matrix of Tournament Variables')
        plt.tight_layout()
        plt.savefig('graphs/correlation_heatmap.png')
        plt.close()
        print('Saved plot: graphs/correlation_heatmap.png')

        # Scatter plot: Median Score vs. Noise by Strategy (use BaseName)
        plt.figure(figsize=(14, 8))
        sns.scatterplot(data=all_data, x='noise', y='Median_score', hue='BaseName', alpha=0.7)
        plt.title('Median Score vs. Noise by Strategy')
        plt.ylabel('Median Score')
        plt.xlabel('Noise')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('graphs/score_vs_noise.png')
        plt.close()
        print('Saved plot: graphs/score_vs_noise.png')

        # Barplot: Number of wins (highest median score) per strategy (use BaseName)
        win_counts = all_data.loc[all_data.groupby(['tournament_type', 'Rank'])['Median_score'].idxmax()]
        win_counts['BaseName'] = win_counts['Name'].apply(extract_base_name)
        win_summary = win_counts['BaseName'].value_counts().sort_values(ascending=False)
        plt.figure(figsize=(12, 6))
        sns.barplot(x=win_summary.index, y=win_summary.values)
        plt.title('Number of Tournament Wins per Strategy (Highest Median Score)')
        plt.ylabel('Number of Wins')
        plt.xlabel('Strategy')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('graphs/strategy_win_counts.png')
        plt.close()
        print('Saved plot: graphs/strategy_win_counts.png')

        # Scatter plot: Cooperation vs. Median Score (use BaseName)
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=all_data, x='Cooperation_rating', y='Median_score', hue='BaseName', alpha=0.7)
        plt.title('Cooperation Rating vs. Median Score by Strategy')
        plt.xlabel('Cooperation Rating')
        plt.ylabel('Median Score')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('graphs/cooperation_vs_score.png')
        plt.close()
        print('Saved plot: graphs/cooperation_vs_score.png')

        # Parameter sensitivity: Score vs. n_strategies (use BaseName)
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=all_data, x='n_strategies', y='Median_score', hue='BaseName', alpha=0.7)
        plt.title('Median Score vs. Number of Strategies in Tournament')
        plt.xlabel('Number of Strategies')
        plt.ylabel('Median Score')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('graphs/score_vs_n_strategies.png')
        plt.close()
        print('Saved plot: graphs/score_vs_n_strategies.png')

        # Robustness: Boxplot of Median Score Std Dev per Strategy (use BaseName)
        score_std = all_data.groupby('BaseName')['Median_score'].std().sort_values(ascending=False)
        plt.figure(figsize=(12, 6))
        sns.barplot(x=score_std.index, y=score_std.values)
        plt.title('Score Standard Deviation per Strategy (Robustness)')
        plt.ylabel('Std Dev of Median Score')
        plt.xlabel('Strategy')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig('graphs/score_std_per_strategy.png')
        plt.close()
        print('Saved plot: graphs/score_std_per_strategy.png')

        # Cooperation vs. Score by Tournament Type (FacetGrid, use BaseName)
        g = sns.FacetGrid(all_data, col='tournament_type', col_wrap=2, height=5, sharex=True, sharey=True)
        g.map_dataframe(sns.scatterplot, x='Cooperation_rating', y='Median_score', hue='BaseName', alpha=0.7)
        g.add_legend()
        g.set_axis_labels('Cooperation Rating', 'Median Score')
        g.fig.suptitle('Cooperation vs. Median Score by Tournament Type', y=1.02)
        plt.tight_layout()
        g.savefig('graphs/cooperation_vs_score_facet.png')
        plt.close()
        print('Saved plot: graphs/cooperation_vs_score_facet.png')

        # --- Advanced: Pairwise Matchup Matrix (Heatmap) ---
    if 'Name' in all_data.columns and 'Opponent' in all_data.columns and 'Median_score' in all_data.columns:
        # Pivot to get average score for each (strategy, opponent) pair
        matchup = all_data.pivot_table(index='Name', columns='Opponent', values='Median_score', aggfunc='mean')
        plt.figure(figsize=(14, 12))
        sns.heatmap(matchup, annot=False, cmap='viridis')
        plt.title('Pairwise Matchup: Average Median Score (Strategy vs. Opponent)')
        plt.ylabel('Strategy')
        plt.xlabel('Opponent')
        plt.tight_layout()
        plt.savefig('graphs/pairwise_matchup_heatmap.png')
        plt.close()
        print('Saved plot: graphs/pairwise_matchup_heatmap.png')
    else:
        print('Pairwise matchup matrix skipped: required columns (Name, Opponent, Median_score) not found.')

    # --- Advanced: Clustering of Strategies (Hierarchical) ---
    if 'BaseName' in all_data.columns and 'Median_score' in all_data.columns and 'tournament_type' in all_data.columns:
        # Create a matrix: rows=base strategies, columns=tournament types, values=mean median score
        perf_matrix = all_data.pivot_table(index='BaseName', columns='tournament_type', values='Median_score', aggfunc='mean').fillna(0)
        from scipy.cluster.hierarchy import linkage, dendrogram
        import numpy as np
        plt.figure(figsize=(10, 6))
        linkage_matrix = linkage(perf_matrix, method='ward')
        dendrogram(linkage_matrix, labels=perf_matrix.index, leaf_rotation=90)
        plt.title('Hierarchical Clustering of Strategies by Performance')
        plt.ylabel('Distance')
        plt.tight_layout()
        plt.savefig('graphs/strategy_clustering_dendrogram.png')
        plt.close()
        print('Saved plot: graphs/strategy_clustering_dendrogram.png')
    else:
        print('Strategy clustering skipped: required columns not found.')

    # --- Correlation between tournament variables and winning strategies ---
    # For each run and tournament type, find the winning strategy (highest mean median score)
    if 'BaseName' in all_data.columns and 'Median_score' in all_data.columns and 'run' in all_data.columns and 'tournament_type' in all_data.columns:
        # Find the winner for each run and tournament type
        winners = all_data.loc[all_data.groupby(['run', 'tournament_type'])['Median_score'].idxmax()]
        # Select relevant columns for correlation
        corr_vars = ['noise', 'prob_end', 'R', 'S', 'T', 'P', 'n_strategies', 'turns', 'repetitions']
        # Encode winning strategy as categorical codes for correlation
        winners = winners.copy()
        winners['WinnerCode'] = winners['BaseName'].astype('category').cat.codes
        # Compute correlation matrix
        corr = winners[corr_vars + ['WinnerCode']].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title('Correlation between Tournament Variables and Winning Strategy (code)')
        plt.tight_layout()
        plt.savefig('graphs/winner_variable_correlation_heatmap.png')
        plt.close()
        print('Saved plot: graphs/winner_variable_correlation_heatmap.png')
    else:
        print('Could not compute winner-variable correlation: required columns not found.')

    # --- Boxplots: Each variable vs. Winning Strategy ---
    if 'BaseName' in all_data.columns and 'Median_score' in all_data.columns and 'run' in all_data.columns and 'tournament_type' in all_data.columns:
        winners = all_data.loc[all_data.groupby(['run', 'tournament_type'])['Median_score'].idxmax()]
        corr_vars = ['noise', 'prob_end', 'R', 'S', 'T', 'P', 'n_strategies', 'turns', 'repetitions']
        for var in corr_vars:
            if var in winners.columns:
                plt.figure(figsize=(14, 8))
                sns.boxplot(data=winners, x='BaseName', y=var)
                plt.title(f'{var} Distribution by Winning Strategy')
                plt.xlabel('Winning Strategy')
                plt.ylabel(var)
                plt.xticks(rotation=90)
                plt.tight_layout()
                plt.savefig(f'graphs/winner_{var}_boxplot.png')
                plt.close()
                print(f'Saved plot: graphs/winner_{var}_boxplot.png')
    else:
        print('Could not create variable-vs-winner boxplots: required columns not found.')

    # --- Pairplot: Joint distribution of payoffs for each winning strategy ---
    if 'BaseName' in all_data.columns and 'Median_score' in all_data.columns and 'run' in all_data.columns and 'tournament_type' in all_data.columns:
        winners = all_data.loc[all_data.groupby(['run', 'tournament_type'])['Median_score'].idxmax()]
        payoff_vars = ['R', 'S', 'T', 'P']
        if all(var in winners.columns for var in payoff_vars):
            import seaborn as sns
            sns.pairplot(winners, vars=payoff_vars, hue='BaseName', corner=True, plot_kws={'alpha':0.7})
            plt.suptitle('Joint Distribution of Payoff Values for Each Winning Strategy', y=1.02)
            plt.tight_layout()
            plt.savefig('graphs/winner_payoff_pairplot.png')
            plt.close()
            print('Saved plot: graphs/winner_payoff_pairplot.png')
        else:
            print('Could not create payoff pairplot: some payoff columns missing.')
    else:
        print('Could not create payoff pairplot: required columns not found.')


