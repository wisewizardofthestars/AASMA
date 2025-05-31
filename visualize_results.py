import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import scipy

# List of result files to visualize
types = ['standard', 'noisy', 'probabilistic', 'prob_noisy']
dfs = []

for t in types:
    filename = os.path.join("csv", f"{t}_aggregated.csv")
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
        plt.savefig(f"graphs/{t}_avg_scores.png")
        plt.close()
        print(f"Saved plot: graphs/{t}_avg_scores.png")
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
        plt.savefig("graphs/score_distribution_boxplot.png")
        plt.close()
        print("Saved plot: graphs/score_distribution_boxplot.png")

        # Grouped barplot: Mean median score per strategy per tournament type
        mean_scores = all_data.groupby(['Name', 'tournament_type'])['Median_score'].mean().reset_index()
        plt.figure(figsize=(16, 8))
        sns.barplot(data=mean_scores, x='Name', y='Median_score', hue='tournament_type')
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

        # Scatter plot: Median Score vs. Noise by Strategy
        plt.figure(figsize=(14, 8))
        sns.scatterplot(data=all_data, x='noise', y='Median_score', hue='Name', alpha=0.7)
        plt.title('Median Score vs. Noise by Strategy')
        plt.ylabel('Median Score')
        plt.xlabel('Noise')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('graphs/score_vs_noise.png')
        plt.close()
        print('Saved plot: graphs/score_vs_noise.png')

        # Barplot: Number of wins (highest median score) per strategy
        win_counts = all_data.loc[all_data.groupby(['tournament_type', 'Rank'])['Median_score'].idxmax()]
        win_summary = win_counts['Name'].value_counts().sort_values(ascending=False)
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

        # Scatter plot: Cooperation vs. Median Score
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=all_data, x='Cooperation_rating', y='Median_score', hue='Name', alpha=0.7)
        plt.title('Cooperation Rating vs. Median Score by Strategy')
        plt.xlabel('Cooperation Rating')
        plt.ylabel('Median Score')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('graphs/cooperation_vs_score.png')
        plt.close()
        print('Saved plot: graphs/cooperation_vs_score.png')

        # Statistical significance: ANOVA for top strategies
        from scipy.stats import f_oneway
        top_strats = all_data['Name'].value_counts().index[:5]
        anova_data = [all_data.loc[all_data['Name'] == strat, 'Median_score'] for strat in top_strats]
        f_stat, p_val = f_oneway(*anova_data)
        with open('graphs/anova_top5.txt', 'w') as f:
            f.write(f"ANOVA F-statistic: {f_stat:.3f}\nP-value: {p_val:.3g}\n")
            f.write(f"Top 5 strategies: {list(top_strats)}\n")
        print('Saved ANOVA results for top 5 strategies to graphs/anova_top5.txt')

        # Parameter sensitivity: Score vs. n_strategies
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=all_data, x='n_strategies', y='Median_score', hue='Name', alpha=0.7)
        plt.title('Median Score vs. Number of Strategies in Tournament')
        plt.xlabel('Number of Strategies')
        plt.ylabel('Median Score')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('graphs/score_vs_n_strategies.png')
        plt.close()
        print('Saved plot: graphs/score_vs_n_strategies.png')

        # Robustness: Boxplot of Median Score Std Dev per Strategy
        score_std = all_data.groupby('Name')['Median_score'].std().sort_values(ascending=False)
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

        # Cooperation vs. Score by Tournament Type (FacetGrid)
        g = sns.FacetGrid(all_data, col='tournament_type', col_wrap=2, height=5, sharex=True, sharey=True)
        g.map_dataframe(sns.scatterplot, x='Cooperation_rating', y='Median_score', hue='Name', alpha=0.7)
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
    if 'Name' in all_data.columns and 'Median_score' in all_data.columns and 'tournament_type' in all_data.columns:
        # Create a matrix: rows=strategies, columns=tournament types, values=mean median score
        perf_matrix = all_data.pivot_table(index='Name', columns='tournament_type', values='Median_score', aggfunc='mean').fillna(0)
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
