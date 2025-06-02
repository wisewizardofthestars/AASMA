import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Load all fixed-payoff tournament results
csv_dir = os.path.join(os.path.dirname(__file__), '../csv')
files = [
    'fixed_standard_aggregated.csv',
    'fixed_noisy_aggregated.csv',
    'fixed_probabilistic_aggregated.csv',
    'fixed_prob_noisy_aggregated.csv',
]
dfs = []
for fname in files:
    fpath = os.path.join(csv_dir, fname)
    if os.path.exists(fpath):
        df = pd.read_csv(fpath)
        df['tournament_type'] = fname.replace('fixed_', '').replace('_aggregated.csv', '')
        dfs.append(df)
if not dfs:
    raise RuntimeError('No fixed-payoff result CSVs found!')
all_df = pd.concat(dfs, ignore_index=True)

# Summary statistics
print('Summary statistics:')
print(all_df.describe(include='all'))

# Mean/median score by strategy and tournament type
mean_scores = all_df.groupby(['Name', 'tournament_type'])['Median_score'].mean().unstack()
print('\nMean median scores by strategy and tournament:')
print(mean_scores)

# Boxplot of normalized rank by tournament type
plt.figure(figsize=(10, 6))
sns.boxplot(x='tournament_type', y='Normalized_rank', data=all_df)
plt.title('Normalized Rank by Tournament Type (Fixed Payoffs)')
plt.savefig(os.path.join('..', 'graphs', 'fixedpayoff_normalized_rank_boxplot.png'))
plt.close()

# Cooperation ratio by strategy
plt.figure(figsize=(12, 6))
sns.boxplot(x='Name', y='Cooperation_rating', data=all_df)
plt.xticks(rotation=90)
plt.title('Cooperation Ratio by Strategy (Fixed Payoffs)')
plt.tight_layout()
plt.savefig(os.path.join('..', 'graphs', 'fixedpayoff_cooperation_by_strategy.png'))
plt.close()

# Correlation heatmap of features
features = ['Median_score', 'Cooperation_rating', 'Normalized_rank', 'memory_usage', 'stochastic', 'makes_use_of_game', 'makes_use_of_length', 'extortion_factor_chi']
plt.figure(figsize=(10, 8))
corr = all_df[features].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title('Feature Correlation Heatmap (Fixed Payoffs)')
plt.tight_layout()
plt.savefig(os.path.join('..', 'graphs', 'fixedpayoff_feature_correlation_heatmap.png'))
plt.close()

# Top strategies by mean normalized rank
top_strats = all_df.groupby('Name')['Normalized_rank'].mean().sort_values().head(10)
print('\nTop 10 strategies by mean normalized rank:')
print(top_strats)

# --- Advanced Analyses ---
# PCA on selected features
pca_features = [f for f in features if f in all_df.columns and all_df[f].notnull().all()]
if len(pca_features) > 2:
    X = all_df[pca_features].values
    X_scaled = StandardScaler().fit_transform(X)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=all_df['Normalized_rank'], cmap='viridis', alpha=0.7)
    plt.colorbar(scatter, label='Normalized Rank')
    plt.title('PCA of Features (Fixed Payoffs)')
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.tight_layout()
    plt.savefig(os.path.join('..', 'graphs', 'fixedpayoff_pca_scatter.png'))
    plt.close()

# Cluster heatmap (optional, if you want to see strategy-feature clustering)
try:
    cluster_data = all_df.groupby('Name')[features].mean().dropna()
    sns.clustermap(cluster_data, cmap='vlag', standard_scale=1, figsize=(12, 10))
    plt.title('Strategy Feature Clustering (Fixed Payoffs)')
    plt.savefig(os.path.join('..', 'graphs', 'fixedpayoff_strategy_clustermap.png'))
    plt.close()
except Exception as e:
    print('Clustermap failed:', e)

# Save summary table
summary_table = all_df.groupby('Name')[['Median_score', 'Cooperation_rating', 'Normalized_rank']].mean().sort_values('Normalized_rank')
summary_table.to_csv(os.path.join('..', 'graphs', 'fixedpayoff_strategy_summary.csv'))

print('\nAnalysis complete. Plots and summary table saved to ../graphs/.')
