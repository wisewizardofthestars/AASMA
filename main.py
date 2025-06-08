import axelrod as axl
import random
from players import non_meta_strategies, meta_strategy_classes
import os
import pandas as pd
import csv
import argparse

def generate_better_pd_payoffs(t_range=(4.0, 6.0), r_range=(2.0, 4.0), p_range=(0.0, 2.0), s_range=(-1.0, 1.0), max_attempts=1000, precision=2):
    """
    Generates valid Prisoner's Dilemma payoffs which are not safe for zero-determinant strategies
    Enforces T > R > P > S and 2R > T + S

    Parameters:
    - t_range: Tuple for (min, max) T value
    - r_range: Tuple for (min, max) R value
    - p_range: Tuple for (min, max) P value
    - s_range: Tuple for (min, max) S value
    - max_attempts: Maximum number of retries before giving up
    - precision: Decimal precision to round results

    Returns:
    - R, S, T, P

    Raises:
    - ValueError if no valid set is found after max_attempts
    """
    for _ in range(max_attempts):
        T = round(random.uniform(*t_range), precision)
        R = round(random.uniform(*r_range), precision)
        P = round(random.uniform(*p_range), precision)
        S = round(random.uniform(*s_range), precision)
        if T > R > P > S and 2 * R > T + S:
            return R, S, T, P
    raise ValueError("Failed to generate valid Prisoner's Dilemma payoffs.")

def run_once(random_payoffs=True, run_number=None, prefix=''):
    if random_payoffs:
        R, S, T, P = generate_better_pd_payoffs() 
        game = axl.Game(r=R, s=S, t=T, p=P)
    else:
        R, S, T, P = 3, 0, 5, 1
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

    config_file = f"{prefix}run_configs.csv"
    write_header = not os.path.exists(config_file)
    with open(config_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['run', 'R', 'S', 'T', 'P', 'noise', 'prob_end', 'repetitions', 'turns', 'n_strategies', 'selected_strategies'])
        writer.writerow([
            run_number,
            R, S, T, P, noise, prob_end, repetitions, turns, n_strategies, '|'.join(selected_names)
        ])

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
        output_file = f"{prefix}{name}_aggregated.csv"
        df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)

    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    player1, player2 = selected_players[0], selected_players[1]
    name1, name2 = repr(player1), repr(player2)

    match = axl.Match((player1, player2), turns=turns, game=game)
    actions = match.play()

    rounds_data = []
    for a1, a2 in actions:
        payoff1, payoff2 = game.score((a1, a2))
        rounds_data.append((a1, a2, payoff1, payoff2))

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

    def update(frame):
        ax1.clear()
        ax2.clear()
        ax3.clear()

        a1, a2, _, _ = rounds_data[frame]
        choices = [1 if a1 == axl.Action.C else 0, 1 if a2 == axl.Action.C else 0]
        colors = ["green" if c else "red" for c in choices]
        action_labels = ["C" if c else "D" for c in choices]

        # Draw bars for actions, but set a minimum visible height for 'C' (cooperate)
        min_height = 0.15
        bar_heights = [c if c else 0 for c in choices]
        # If cooperate (1), set to 1; if defect (0), set to min_height for visibility
        visible_heights = [h if h > 0 else min_height for h in bar_heights]
        bars = ax1.bar([name1, name2], visible_heights, color=colors)
        ax1.set_ylim(0, 1)
        ax1.set_yticks([0, 1])
        ax1.set_yticklabels(["D", "C"])
        ax1.set_title(f"Round {frame + 1}: Actions")
        for i, (bar, label) in enumerate(zip(bars, action_labels)):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, label, ha='center', va='bottom', fontsize=12)

        payoff1 = sum(r[2] for r in rounds_data[:frame + 1])
        payoff2 = sum(r[3] for r in rounds_data[:frame + 1])
        ax2.bar([name1, name2], [payoff1, payoff2], color=["blue", "orange"])
        ax2.set_title("Cumulative Payoffs")
        for i, val in enumerate([payoff1, payoff2]):
            ax2.text(i, val + 0.05, f"{val:.2f}", ha='center', va='bottom', fontsize=12)

        history1 = [1 if r[0] == axl.Action.C else 0 for r in rounds_data[:frame + 1]]
        history2 = [1 if r[1] == axl.Action.C else 0 for r in rounds_data[:frame + 1]]
        ax3.plot(range(1, frame + 2), history1, marker='o', label=name1, color="green")
        ax3.plot(range(1, frame + 2), history2, marker='o', label=name2, color="red")
        ax3.set_yticks([0, 1])
        ax3.set_yticklabels(["D", "C"])
        ax3.set_xlabel("Round")
        ax3.set_ylabel("Action")
        ax3.set_title("Action History")
        ax3.legend(loc="upper right")

        plt.suptitle(
            f"{name1} vs {name2} | Payoffs: R={R}, S={S}, T={T}, P={P} | Noise={noise}, Prob_end={prob_end}, Turns={turns}",
            fontsize=10
        )

    ani = animation.FuncAnimation(fig, update, frames=len(rounds_data), repeat=False)
    plt.tight_layout(rect=[0, 0, 1, 0.94])  
    video_filename = f"{prefix}run_{run_number}_match_animation.mp4"
    try:
        from matplotlib.animation import FFMpegWriter
        ani.save(video_filename, writer=FFMpegWriter(fps=1), dpi=200)
        print(f"Saved animation to {video_filename}")
    except Exception as e:
        print(f"Could not save animation as .mp4: {e}\nTry installing ffmpeg and ensure it is in your PATH.")
    # END animation block


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Run Axelrod tournament simulations.")
    parser.add_argument(
    "--no-random-payoffs",
    action="store_false",
    dest="random_payoffs",
    help="Use fixed payoffs instead of randomly generated ones (default: true)."
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1000,
        help="Number of runs to execute (default: 1000)."
    )
    parser.add_argument(
    "--filename",
    type=str,
    default="csv/",
    help="Prefix to use for all result and config CSV filenames (default: csv/)."
    )
    args = parser.parse_args()

    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)

    total_runs = args.runs

    prefix = args.filename
    files = [f"{prefix}run_configs.csv", f"{prefix}standard_aggregated.csv", f"{prefix}noisy_aggregated.csv", 
             f"{prefix}probabilistic_aggregated.csv", f"{prefix}prob_noisy_aggregated.csv"]
    for file in files:        
        if os.path.exists(file):
            os.remove(file)

    for i in range(1, total_runs + 1):
        print(f" Run {i}/{total_runs}")
        run_once(random_payoffs=args.random_payoffs, run_number=i, prefix=prefix)
