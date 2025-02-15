import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

initial_bankroll = 1000
bet_percentage = 0.01
odds = 2.5
winning_prob = 0.42
losing_prob = 0.58
num_bets = 100
num_sims = 500

def run_simulation():
    bankroll = initial_bankroll
    bankroll_hostory = [bankroll]

    for _ in range(num_bets):
        bet_amount = bankroll*bet_percentage
        if np.random.rand() < winning_prob:
            bankroll += bet_amount * (odds-1)
        else:
            bankroll -= bet_amount
        bankroll_hostory += bankroll_hostory

    return bankroll_hostory

all_simulations = [run_simulation() for _ in tqdm(range(num_sims))]

all_sims_sorted = sorted(all_simulations, key=lambda x: x[-1])
sims_to_plot = all_sims_sorted[1] + all_sims_sorted[len(all_sims_sorted)//2] + all_sims_sorted[-1]


plt.figure(figsize=(10,6))

for sim in sims_to_plot:
    plt.plot(sim, color="blue", alpha=0.2)

plt.title("Monte Carlo Sim")
plt.xlabel("Bet number")
plt.ylabel("Bankroll")
plt.grid(True)
plt.show()