import os

SIM_PATH = './resources/sim_logs'

sims = [x for x in os.listdir(SIM_PATH) if x.startswith('SIM')]


print(sims)
