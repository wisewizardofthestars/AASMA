import sys
import numpy as np
import pandas as pd
import axelrod as axl


def get_least_squares(vector, game=axl.game.Game()):
    """
    Obtain the least squares directly

    Returns:

    - xstar
    - residual
    """

    R, P, S, T = game.RPST()

    C = np.array([[R - P, R - P], [S - P, T - P], [T - P, S - P], [0, 0]])

    tilde_p = np.array([vector[0] - 1, vector[1] - 1, vector[2], vector[3]])

    xstar = np.linalg.inv(C.transpose() @ C) @ C.transpose() @ tilde_p

    SSError = tilde_p.transpose() @ tilde_p - tilde_p @ C @ xstar

    return SSError


def get_memory_percentage(row):
    if np.isinf(row["Memory_depth"]):
        return 1
    if row["Memory_depth"] == 0:
        return 0
    return row["Memory_depth"] / row["turns"]


def fix_fsm_memory(row):
    if "FSM" in row["Name"]:
        return np.inf
    else:
        return row["Memory_depth"]


def fix_name(row):
    name = row["Name"]
    if "Hard Go By Majority:" in name:
        return "".join(name.split(":"))
    if "Soft Go By Majority:" in name:
        return "".join(name.split(":"))
    return name.split(":")[0]


def get_error_for_row(row):
    columns_for_sse = [
        "CC_to_C_rate",
        "CD_to_C_rate",
        "DC_to_C_rate",
        "DD_to_C_rate",
    ]
    vector = [row.get(column, 0) for column in columns_for_sse]
    sse_error = get_least_squares(vector=vector)

    return sse_error


def get_cluster_on(row, percentage):
    value = row["Normalized_rank"] <= percentage
    return int(value)


def get_cooporation_rating_compared_to_max(row):
    return row["Cooperation_rating"] / row["Cooperation_rating_max"]


def get_cooporation_rating_compared_to_median(row):
    return row["Cooperation_rating"] / row["Cooperation_rating_median"]


def get_cooporation_rating_compared_to_mean(row):
    return row["Cooperation_rating"] / row["Cooperation_rating_mean"]


def get_cooporation_rating_compared_to_min(row):
    if row["Cooperation_rating_min"] == 0:
        return row["Cooperation_rating_min"]
    return row["Cooperation_rating_min"] / row["Cooperation_rating"]


if __name__ == "__main__":

    file = sys.argv[1]
    output = file.replace(".csv", "_processed.csv")

    df = pd.read_csv(file)

    print("Processing")
    df["SSE"] = df.apply(get_error_for_row, axis=1)
    df["Name"] = df.apply(fix_name, axis=1)

    percentages = [0.05, 0.25, 0.5]
    for percentage in percentages:
        df[f"cluster_on_{percentage}"] = df.apply(
            get_cluster_on, args=(percentage,), axis=1
        )
    # Group by run (or seed if you prefer) for cooperation stats
    max_coop = df.groupby("run")["Cooperation_rating"].max().rename(
        "Cooperation_rating_max"
    )
    df = pd.merge(
        df, max_coop, left_on="run", right_index=True, how="left", sort=False
    )

    min_coop = df.groupby("run")["Cooperation_rating"].min().rename(
        "Cooperation_rating_min"
    )
    df = pd.merge(
        df, min_coop, left_on="run", right_index=True, how="left", sort=False
    )

    median_coop = df.groupby("run")["Cooperation_rating"].median().rename(
        "Cooperation_rating_median"
    )
    df = pd.merge(
        df, median_coop, left_on="run", right_index=True, how="left", sort=False
    )

    mean_coop = df.groupby("run")["Cooperation_rating"].mean().rename(
        "Cooperation_rating_mean"
    )
    df = pd.merge(
        df, mean_coop, left_on="run", right_index=True, how="left", sort=False
    )

    df["Cooperation_rating_comp_to_max"] = df.apply(
        get_cooporation_rating_compared_to_max, axis=1
    )
    df["Cooperation_rating_comp_to_min"] = df.apply(
        get_cooporation_rating_compared_to_min, axis=1
    )
    df["Cooperation_rating_comp_to_median"] = df.apply(
        get_cooporation_rating_compared_to_median, axis=1
    )
    df["Cooperation_rating_comp_to_mean"] = df.apply(
        get_cooporation_rating_compared_to_mean, axis=1
    )
    # If memory depth exists, fix FSM memory and memory usage
    if "Memory_depth" in df.columns:
        df["Memory_depth"] = df.apply(fix_fsm_memory, axis=1)
    if "turns" in df.columns and "Memory_depth" in df.columns:
        df["memory_usage"] = df.apply(get_memory_percentage, axis=1)

    print(f"Writing to file {output}")
    df.to_csv(output, index=False)