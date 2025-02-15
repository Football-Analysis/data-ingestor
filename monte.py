import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

initial_bankroll = 1000
bet_percentage = 0.01
odds = 2.5
edge = 0.05
winning_prob = (1/odds)*(1+edge)
losing_prob = 0.58
num_bets = 2400
num_sims = 100000

def run_simulation():
    bankroll = initial_bankroll
    bankroll_hostory = [bankroll]

    for _ in range(num_bets):
        bet_amount = bankroll*bet_percentage
        if np.random.rand() < winning_prob:
            bankroll += bet_amount * (odds-1)
        else:
            bankroll -= bet_amount
        bankroll_hostory.append(bankroll)

    return bankroll_hostory

all_simulations = [run_simulation() for _ in tqdm(range(num_sims))]
all_simulations.sort(key=lambda x: int(x[-1]))
sims_to_plot = []
sims_to_plot.append(all_simulations[0])
sims_to_plot.append(all_simulations[len(all_simulations)//2])
sims_to_plot.append(all_simulations[-1])


print("BEST, MEAN and WORST CASE")
worst = all_simulations[0][-1]
mean = all_simulations[len(all_simulations)//2][-1]
best = all_simulations[-1][-1]
print("95% CONFIDENCE LEVEL BETWEEN")
low_percentile = all_simulations[int(len(all_simulations)*0.025)][-1]
high_percentile = all_simulations[int(len(all_simulations)*0.975)][-1]

plt.figure(figsize=(10,6))

for sim in sims_to_plot:
    plt.plot(sim, color="blue", alpha=0.2)

plt.plot(all_simulations[int(len(all_simulations)*0.025)], color="red")
plt.plot(all_simulations[int(len(all_simulations)*0.975)], color="red")

plt.title(f"{num_sims}S, {num_bets}B, {edge}E - {best}B, {mean}M, {worst}W - 95% [{low_percentile}, {high_percentile}]")
plt.xlabel("Bet number")
plt.ylabel("Bankroll")
plt.grid(True)

plt.savefig(f'{num_sims}-simulations-{num_bets}-bets-{edge}-edge.png')
