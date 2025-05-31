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

meta_strategy_classes = [axl.MetaMixer, axl.MetaWinner]