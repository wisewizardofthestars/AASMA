import os
import pandas as pd
import statsmodels.api as sm


csv_paths = [
    "../csv/noisy_aggregated.csv",
    "../csv/prob_noisy_aggregated.csv",
    "../csv/probabilistic_aggregated.csv",
    "../csv/standard_aggregated.csv",
]

df_list = [pd.read_csv(path) for path in csv_paths]
merged_df = pd.concat(df_list, ignore_index=True)

merged_df.to_csv("all_tournaments_merged.csv", index=False)
print("Merged CSV saved as all_tournaments_merged.csv")



def run_regression(df: pd.DataFrame, features: list, target_col: str) -> pd.DataFrame:
    """
    Runs an OLS regression of `target_col` on `features` (plus constant)
    and returns a tidy DataFrame containing:
      - coefficient ("coef")
      - standard error ("std_err")
      - t‐stat ("t")
      - p‐value ("p_value")
      - [optionally R² repeated for each row so we can see it alongside]
    """
    df_clean = df.dropna(subset=features + [target_col]).copy()
    if df_clean.empty:
        return pd.DataFrame() 

    X = df_clean[features]
    y = df_clean[target_col]

    X_with_const = sm.add_constant(X)

    model = sm.OLS(y, X_with_const).fit()

    coef_table = model.summary2().tables[1].copy()

    coef_table = coef_table.rename(
        columns={
            "Coef.": "coef",
            "Std.Err.": "std_err",
            "t": "t_stat",
            "P>|t|": "p_value",
        }
    )

    coef_table["r_squared"] = round(model.rsquared, 5)
    coef_table["adj_r_squared"] = round(model.rsquared_adj, 5)
    coef_table["n_obs"] = int(model.nobs)

    coef_table = coef_table.reset_index().rename(columns={"index": "feature"})

    return coef_table



input_path = "all_tournaments_merged.csv"
df_all = pd.read_csv(input_path)

features = [
    "CC_to_C_rate",
    "CD_to_C_rate",
    "DC_to_C_rate",
    "Cooperation_rating",
    # add more i think??
]

target_column = "Median_score"


regression_results = {}

for ttype in sorted(df_all["tournament"].unique()):
    df_tt = df_all[df_all["tournament"] == ttype].copy()

    tidy_df = run_regression(df_tt, features, target_column)
    if tidy_df.empty:
        print(f"→ No data (or all NaNs) for tournament: {ttype}")
        continue

    tidy_df["tournament"] = ttype

    tidy_df = tidy_df.set_index(["tournament", "feature"])
    regression_results[ttype] = tidy_df


if regression_results:
    combined_df = pd.concat(regression_results.values(), axis=0)

    combined_df = combined_df.sort_index(level=["tournament", "feature"])

    # Save to CSV
    out_csv = os.path.join("regression_summary.csv")
    combined_df.to_csv(out_csv)
    print(f"Regression summary saved to {out_csv}")

    pd.set_option("display.max_rows", None)
    print("\nCombined regression results (first few rows):\n")
    print(combined_df.head(21))
else:
    print("No regression results to save.")