import axelrod as axl

# Strategy groups
basic_strategies = axl.basic_strategies
memory1_strategies = [axl.GTFT, axl.Grudger]
memory2_strategies = [axl.TitFor2Tats, axl.DoubleCrosser]
stochastic_strategies = [axl.SoftJoss, axl.Random]
zero_determinant_strategies = [axl.ZDExtort2, axl.ZDGTFT2]
rl_strategies = [axl.EvolvedHMM5, axl.EvolvedFSM16]

# Temporarily exclude meta strategies
non_meta_strategies = (
    basic_strategies + memory1_strategies + memory2_strategies +
    stochastic_strategies + zero_determinant_strategies + rl_strategies
)

# Instantiate non-meta players
non_meta_players = [s() for s in non_meta_strategies]

# Prepare meta strategies using only the above strategies
meta_strategies = [
    axl.MetaMixer(team=non_meta_strategies),
    axl.MetaWinner(team=non_meta_strategies)
]

# Combine all players
players = non_meta_players + meta_strategies

# Optional: sort players by name
players.sort(key=lambda p: repr(p))

# Print for confirmation
print('Num_players:', len(players))
print(players)