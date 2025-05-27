import axelrod as axl
import random
from players import players
import os
import pandas as pd

# Generate valid PD payoffs
def generate_pd_payoffs(t_range=(4.0, 6.0), max_attempts=1000, precision=2):
    """
    Generates valid Prisoner's Dilemma payoffs without artificial buffers:
    Enforces T > R > P > S and 2R > T + S

    Parameters:
    - t_range: Tuple for (min, max) temptation value (T)
    - max_attempts: Maximum number of retries before giving up
    - precision: Decimal precision to round results

    Returns:
    - Tuple (R, S, T, P)

    Raises:
    - ValueError if no valid set is found after max_attempts
    """
    for _ in range(max_attempts):
        T = random.uniform(*t_range)
        R = random.uniform(2.0, T)
        P = random.uniform(1.0, R)
        S = random.uniform(0.0, P)

        # Strict inequality and strategic condition
        if T > R > P > S and 2 * R > T + S:
            return tuple(round(x, precision) for x in (R, S, T, P))

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
    raise ValueError("Unable to generate payoffs valid for ZD strategies after many attempts.")

def run_once():
    R, S, T, P = generate_pd_payoffs_zd_safe() 
    game = axl.Game(r=R, s=S, t=T, p=P)

    noise = round(random.uniform(0, 0.1), 2)
    prob_end = round(random.uniform(0, 0.1), 2)
    repetitions = random.randint(10, 100)
    turns = random.randint(1, 200)

    # Randomly select a subset of strategies for this run
    n_strategies = random.randint(2, len(players))
    selected_players = random.sample(players, n_strategies)

    # Print configuration info
    print(f"Payoffs - R: {R}, S: {S}, T: {T}, P: {P}")
    print(f"Noise: {noise}")
    print(f"Proability ending: {prob_end}")
    print(f"Repetitions: {repetitions}")
    print(f"Turns: {turns}")
    print(f"Number of strategies: {n_strategies}")
    print(f"Selected strategies: {[repr(p) for p in selected_players]}")

    tournaments = {
        'standard': axl.Tournament(selected_players, game=game, repetitions=repetitions, turns=turns),
        'noisy': axl.Tournament(selected_players, game=game, noise=noise, repetitions=repetitions, turns=turns),
        'probabilistic': axl.Tournament(selected_players, game=game, prob_end=prob_end, repetitions=repetitions, turns=turns),
        'prob_noisy': axl.Tournament(selected_players, game=game, noise=noise, prob_end=prob_end, repetitions=repetitions, turns=turns)
    }

    results = {}

    for name, tourn in tournaments.items():
        res = tourn.play(processes=os.cpu_count())
        summary_list = res.summarise()
        df = pd.DataFrame(summary_list)
        #df =res.summarise()
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
        results[name] = df
    return results

if __name__ == "__main__":
    # We got to set a random seed for reproducibility
    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)

    runs = 10
    agg = {key: [] for key in ['standard', 'noisy', 'probabilistic', 'prob_noisy']}

    for i in range(1, runs + 1):
        print(f"Run {i}/{runs}")
        out = run_once()
        for key, df in out.items():
                agg[key].append(df)
    
    for key,dfs in agg.items():
        full = pd.concat(dfs, ignore_index=True)
        filename = f"{key}_aggregated.csv"
        full.to_csv(filename, index=False)
        print(f"Results saved to {filename}")


    # Create tournaments
    #standard_tournament = axl.Tournament(players, game=game, repetitions=repetitions, turns=turns)
    #noisy_tournament = axl.Tournament(players, game=game, noise=noise, repetitions=repetitions, turns=turns)
    #prob_tournament = axl.Tournament(players, game=game, prob_end=prob_end, repetitions=repetitions, turns=turns)
    #prob_noisy_tournament = axl.Tournament(players, game=game, noise=noise, prob_end=prob_end, repetitions=repetitions, turns=turns)

# Run tournaments
#standard_results = standard_tournament.play(processes=os.cpu_count())
#noisy_results = noisy_tournament.play(processes=os.cpu_count())
#prob_results = prob_tournament.play(processes=os.cpu_count())
#prob_noisy_results = prob_noisy_tournament.play(processes=os.cpu_count())

# Get results summary
#standard_results.write_summary('standard_summary.csv')
#noisy_results.write_summary('noisy_summary.csv')
#prob_results.write_summary('prob_summary.csv')
#prob_noisy_results.write_summary('prob_noisy_summary.csv')

# Plot results only of prob noisy
# plot = axl.Plot(prob_noisy_results)
# p = plot.save_all_plots(prefix="../../../../random", title_prefix="random")