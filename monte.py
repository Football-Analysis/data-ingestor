import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from random import uniform

initial_bankroll = 1000
default_bet_percentage = 0.02
# odds = 2.5
#edge = 0.05
#winning_prob = (1/odds)*(1+edge)
num_bets = 2400
num_sims = 100000

def run_simulation():
    bankroll = initial_bankroll
    bankroll_hostory = [bankroll]

    for _ in range(num_bets):
        odds = uniform(1.1, 6.0)
        edge = uniform(0.05, 0.20)
        winning_prob = (1/odds)*(1+edge)
        sizing_refactor = 2/odds
        confidence_refactor = odds/0.1
        bet_percentage = default_bet_percentage * (sizing_refactor*confidence_refactor)
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
worst = int(all_simulations[0][-1])
mean = int(all_simulations[len(all_simulations)//2][-1])
best = int(all_simulations[-1][-1])
print("95% CONFIDENCE LEVEL BETWEEN")
low_percentile = int(all_simulations[int(len(all_simulations)*0.025)][-1])
high_percentile = int(all_simulations[int(len(all_simulations)*0.975)][-1])

plt.figure(figsize=(10,6))

for sim in sims_to_plot:
    plt.plot(sim, color="blue", alpha=0.2)

plt.plot(all_simulations[int(len(all_simulations)*0.025)], color="red")
plt.plot(all_simulations[int(len(all_simulations)*0.975)], color="red")

plt.title(f"{num_sims}S, {num_bets}B, {edge}E - {best}B, {mean}M, {worst}W - 95% [{low_percentile}, {high_percentile}]")
plt.xlabel("Bet number")
plt.ylabel("Bankroll")
plt.grid(True)

plt.savefig(f'{num_sims}-simulations-{num_bets}-bets-{edge}-edge-adj-sizing-with-odds.png')
