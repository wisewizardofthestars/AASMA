import axelrod as axl
import random
from players import non_meta_strategies, meta_strategy_classes
import os
import pandas as pd
import csv

def generate_pd_payoffs(t_range=(4.0, 6.0), max_attempts=1000, precision=2):
    """
    Generates valid Prisoner's Dilemma payoffs without artificial buffers:
    Enforces T > R > P > S and 2R > T + S

    Parameters:
    - t_range: Tuple for (min, max) temptation value (T)
    - max_attempts: Maximum number of retries before giving up
    - precision: Decimal precision to round results

    Returns:
    - R, S, T, P

    Raises:
    - ValueError if no valid set is found after max_attempts
    """
    for _ in range(max_attempts):
        T = round(random.uniform(*t_range), precision)
        R = round(random.uniform(2.0, T), precision)
        P = round(random.uniform(1.0, R), precision)
        S = round(random.uniform(0.0, P), precision)
        if T > R > P > S and 2 * R > T + S:
            return R, S, T, P
    raise ValueError("Failed to generate valid Prisoner's Dilemma payoffs.")

def generate_pd_payoffs_zd_safe():
    max_attempts = 1000
    for _ in range(max_attempts):
        R, S, T, P = generate_pd_payoffs()
        game = axl.Game(r=R, s=S, t=T, p=P)
        try:
            # instantiate zero determinant strategies to check
            player1 = axl.ZDExtort2()
            player1.set_match_attributes(game=game)

            player2 = axl.ZDGTFT2()
            player2.set_match_attributes(game=game)
            return R, S, T, P
        except ValueError:
            continue
    raise ValueError("Unable to generate payoffs valid for ZD strategies.")

def run_once(run_number=None):
    R, S, T, P = generate_pd_payoffs_zd_safe() 
    game = axl.Game(r=R, s=S, t=T, p=P)

    noise = round(random.uniform(0, 0.1), 2)
    prob_end = round(random.uniform(0, 0.1), 2)
    repetitions = random.randint(10, 100)
    turns = random.randint(1, 200)

    # Randomly select a subset of strategies for this run
    #But not every strategy faces every other in every run!
    all_strategy_classes = non_meta_strategies + meta_strategy_classes
    n_strategies = random.randint(3, len(all_strategy_classes))
    selected_classes = random.sample(all_strategy_classes, n_strategies)
    base_classes = [cls for cls in selected_classes if cls in non_meta_strategies]

   # selected_classes = all_strategy_classes
    #n_strategies = len(selected_classes)

    #base_classes = [cls for cls in all_strategy_classes if cls in non_meta_strategies]

    selected_players = []
    for cls in selected_classes:
        if cls in meta_strategy_classes:
            player = cls(team=base_classes)
        else:
            player = cls()
        selected_players.append(player)

    selected_names = [repr(p) for p in selected_players]

    # Save run configuration to CSV
    config_file = 'run_configs.csv'
    write_header = not os.path.exists(config_file)
    with open(config_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['run', 'R', 'S', 'T', 'P', 'noise', 'prob_end', 'repetitions', 'turns', 'n_strategies', 'selected_strategies'])
        writer.writerow([
            run_number,
            R, S, T, P, noise, prob_end, repetitions, turns, n_strategies, '|'.join(selected_names)
        ])

    # Print configuration info
    print(f"Payoffs - R: {R}, S: {S}, T: {T}, P: {P}")
    print(f"Noise: {noise}")
    print(f"Proability ending: {prob_end}")
    print(f"Repetitions: {repetitions}")
    print(f"Turns: {turns}")
    print(f"Number of strategies: {n_strategies}")
    print(f"Selected strategies: {selected_names}")

    tournaments = {
        'standard': axl.Tournament(selected_players, game=game, repetitions=repetitions, turns=turns),
        'noisy': axl.Tournament(selected_players, game=game, noise=noise, repetitions=repetitions, turns=turns),
        'probabilistic': axl.Tournament(selected_players, game=game, prob_end=prob_end, repetitions=repetitions, turns=turns),
        'prob_noisy': axl.Tournament(selected_players, game=game, noise=noise, prob_end=prob_end, repetitions=repetitions, turns=turns)
    }

    for name, tourn in tournaments.items():
        res = tourn.play(processes=os.cpu_count())
        df = pd.DataFrame(res.summarise())
        df['R'] = R
        df['S'] = S
        df['T'] = T
        df['P'] = P
        df['noise'] = noise
        df['prob_end'] = prob_end
        df['repetitions'] = repetitions
        df['turns'] = turns
        df['tournament'] = name
        df['n_strategies'] = n_strategies
        df['run'] = run_number
        # payoff_matrix = res.payoff_matrix
        # player_names = [repr(p) for p in tourn.players]
        # rows = []
        # for i, name_i in enumerate(player_names):
        #     for j, name_j in enumerate(player_names):
        #         if i == j:
        #             continue  # skip self-play
        #         rows.append({
        #             'Name': name_i,
        #             'Opponent': name_j,
        #             'Median_score': payoff_matrix[i][j],
        #             'R': R,
        #             'S': S,
        #             'T': T,
        #             'P': P,
        #             'noise': noise,
        #             'prob_end': prob_end,
        #             'repetitions': repetitions,
        #             'turns': turns,
        #             'tournament': name,
        #             'n_strategies': n_strategies,
        #             'run': run_number
        #         })
        # df = pd.DataFrame(rows)
        df.to_csv(f"{name}_aggregated.csv", mode='a', header=not os.path.exists(f"{name}_aggregated.csv"), index=False)
#forma como fazem no código do paper
"""       # Compute additional features for each strategy
        # Normalized rank (r)
        df = df.sort_values('Median_score', ascending=False).reset_index(drop=True)
        N = len(df)
        df['Rank'] = df.index
        df['Normalized_rank'] = df['Rank'] / (N - 1) if N > 1 else 0
        # Cooperation ratio (C_r)
        if 'Cooperation_rating' not in df.columns:
            # Try to compute if not present
            if 'Cooperations' in df.columns and 'Turns' in df.columns:
                df['Cooperation_rating'] = df['Cooperations'] / df['Turns']
        # Transition rates and memory usage
        CC_to_C = []
        CD_to_C = []
        DC_to_C = []
        DD_to_C = []
        memory_usage = []
        stochastic = []
        makes_use_of_game = []
        makes_use_of_length = []
        for name in df['Name']:
            # Find the player object
            player = None
            for p in selected_players:
                if repr(p) == name:
                    player = p
                    break
            if player is not None:
                # Use strategy_classifier for meta info
                classifier = getattr(player, 'classifier', player.strategy_classifier())
                stochastic.append(classifier.get('stochastic', False))
                makes_use_of_game.append(classifier.get('makes_use_of_game', False))
                makes_use_of_length.append(classifier.get('makes_use_of_length', False))
                # Memory usage: memory_depth / turns
                mem_depth = getattr(player, 'memory_depth', None)
                if mem_depth is not None and turns > 0:
                    memory_usage.append(mem_depth / turns)
                else:
                    memory_usage.append(None)
                # Transition rates: use state_distribution if available
                try:
                    sd = player.state_distribution
                    CC = sd.get(('C', 'C'), 0)
                    CD = sd.get(('C', 'D'), 0)
                    DC = sd.get(('D', 'C'), 0)
                    DD = sd.get(('D', 'D'), 0)
                    # Next move after each state
                    CC_C = player._state_to_action.get(('C', 'C', 'C'), 0)
                    CD_C = player._state_to_action.get(('C', 'D', 'C'), 0)
                    DC_C = player._state_to_action.get(('D', 'C', 'C'), 0)
                    DD_C = player._state_to_action.get(('D', 'D', 'C'), 0)
                    CC_to_C.append(CC_C / CC if CC > 0 else None)
                    CD_to_C.append(CD_C / CD if CD > 0 else None)
                    DC_to_C.append(DC_C / DC if DC > 0 else None)
                    DD_to_C.append(DD_C / DD if DD > 0 else None)
                except Exception:
                    CC_to_C.append(None)
                    CD_to_C.append(None)
                    DC_to_C.append(None)
                    DD_to_C.append(None)
            else:
                stochastic.append(None)
                makes_use_of_game.append(None)
                makes_use_of_length.append(None)
                memory_usage.append(None)
                CC_to_C.append(None)
                CD_to_C.append(None)
                DC_to_C.append(None)
                DD_to_C.append(None)
        df['CC_to_C_rate'] = CC_to_C
        df['CD_to_C_rate'] = CD_to_C
        df['DC_to_C_rate'] = DC_to_C
        df['DD_to_C_rate'] = DD_to_C
        df['memory_usage'] = memory_usage
        df['stochastic'] = stochastic
        df['makes_use_of_game'] = makes_use_of_game
        df['makes_use_of_length'] = makes_use_of_length
        # Calculate extortion factor (chi) and SSE for each strategy
        extortion_factor_chi = []
        extortion_SSE = []
        # For each strategy, collect (self, opponent) average payoffs
        payoff_matrix = res.payoff_matrix if hasattr(res, 'payoff_matrix') else None
        for idx, name in enumerate(df['Name']):
            if payoff_matrix is not None:
                # Exclude self-play
                self_payoffs = []
                opp_payoffs = []
                for j in range(len(df['Name'])):
                    if j == idx:
                        continue
                    self_payoffs.append(payoff_matrix[idx][j])
                    opp_payoffs.append(payoff_matrix[j][idx])
                if len(self_payoffs) > 1:
                    # Fit line: self = chi * opp + intercept
                    import numpy as np
                    from sklearn.linear_model import LinearRegression
                    X = np.array(opp_payoffs).reshape(-1, 1)
                    y = np.array(self_payoffs)
                    reg = LinearRegression().fit(X, y)
                    chi = reg.coef_[0]
                    y_pred = reg.predict(X)
                    sse = np.sum((y - y_pred) ** 2)
                    extortion_factor_chi.append(chi)
                    extortion_SSE.append(sse)
                else:
                    extortion_factor_chi.append(None)
                    extortion_SSE.append(None)
            else:
                extortion_factor_chi.append(None)
                extortion_SSE.append(None)
        df['extortion_factor_chi'] = extortion_factor_chi
        df['extortion_SSE'] = extortion_SSE"""

if __name__ == "__main__":
    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)

    total_runs = 1000

    for file in ['run_configs.csv', 'standard_aggregated.csv', 'noisy_aggregated.csv', 'probabilistic_aggregated.csv', 'prob_noisy_aggregated.csv']:
        if os.path.exists(file):
            os.remove(file)

    for i in range(1, total_runs + 1):
        print(f" Run {i}/{total_runs}")
        run_once(run_number=i)
