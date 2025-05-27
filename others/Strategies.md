10 to 15 strategies to choose from the ones on the paper
The paper focuses on memory-n strategies in the Prisoner’s Dilemma (OU seja strategies that consider the last n moves of the opponent):

Memory-1 (ou seja consideram só a última ação):
- TitForTat (uma das mais conhecidas)
- Generous TitForTat (GTFT) (Forgives defections with a certain probability, basicamente uma versão mais generosa de TFT)
- WinStayLoseShift (Pavlov) (Repeats action if rewarded (win/stay), switches if punished (lose/shift), supostamente é uma boa estratégia em ambientes com muito noise)
- Grudger (Grim Trigger) (Cooperates until the opponent defects, then defects forever.; basicamente não forgives nunca)

Memory-2:
- TitForTwoTats (basicamente TFT mas só retalia depois de duas defections)
- DoubleCrosser (Cooperates until the opponent defects, then requires two consecutive Cs to revert. basicamente)
- FoolMeOnce ( Defects permanently if the opponent defects twice in any history., é o Grim Trigger mas com memory-2)


Stochastic/Noise-Resistant Strategies:
- Soft Joss (TitForTat but with 10% chance to defect.)Tests robustness to randomness.
- Random (p=0.5) Baseline for stochastic behavior. o deepseek disse que poderiamos por mais interessante se: Use p=0.7 to bias toward cooperation.

Zero-Determinant (ZD) Strategies (Advanced):
- ZDExtort2 (Extorts opponents by enforcing a linear payoff relationship.) basicamente é mais útil só para avaliarmos o evolutionary payoff mas o paper não testa isto por isso só se for um extra
- ZDGTFT-2 (Zero-Determinant Generous TitForTat.)

Meta-Strategies (Adaptive):
- MetaMixer (Randomly selects sub-strategies during play.) : Tests adaptability in heterogeneous populations.
- Champion (Hybrid of TitForTat and aggressive strategies.) se não me engano ganhou um dos torneios

Podemos ou não usar as meta-strategies


