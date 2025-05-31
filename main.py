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
    all_strategy_classes = non_meta_strategies + meta_strategy_classes
    n_strategies = random.randint(3, len(all_strategy_classes))
    selected_classes = random.sample(all_strategy_classes, n_strategies)

    base_classes = [cls for cls in selected_classes if cls in non_meta_strategies]

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
        df.to_csv(f"{name}_aggregated.csv", mode='a', header=not os.path.exists(f"{name}_aggregated.csv"), index=False)

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
