import csv
import os
import sys
from typing import List

import matplotlib.pyplot as plt

from src.domain.human import Fatigue_Profile, FreeWill_Profile
from src.domain.layout import Point
from src.mgr.upp_mgr import Upp_Mgr


def get_conf_id(file):
    return int(file.split('_')[1])


SCENARIO = sys.argv[1]
upp_mgr = Upp_Mgr()
CSV_FILE = upp_mgr.UPPAAL_OUT_PATH.format(SCENARIO).replace('.txt', '.csv')
logs = [file.split('_')[1] for i, file in
        enumerate(os.listdir(upp_mgr.UPPAAL_OUT_PATH.replace('/{}.txt', '/norun_bound_20pts/')))]
uppaal_logs = [file for file in os.listdir(upp_mgr.UPPAAL_OUT_PATH.replace('/{}.txt', '/norun_bound_20pts/')) if
               file.startswith('DPa')]
uppaal_logs.sort(key=get_conf_id)

# Performance analysis
perf_data = []
for i, file in enumerate(uppaal_logs):
    with open(upp_mgr.UPPAAL_OUT_PATH.replace('/{}.txt', '/norun_bound_20pts/') + file) as uppaal_log:
        lines = uppaal_log.readlines()
        runs = list(filter(lambda l: l.__contains__('Pr(<> ...) in'), lines))[0].split(' runs')[0].replace('(', '')
        states = list(filter(lambda l: l.__contains__('States explored'), lines))[0].split(' : ')[1].replace(
            ' states\n', '')
        time = list(filter(lambda l: l.__contains__('CPU user time used'), lines))[0].split(' : ')[1].replace(' ms\n',
                                                                                                              '')
        virt_mem = list(filter(lambda l: l.__contains__('Virtual memory used'), lines))[0].split(' : ')[1].replace(
            ' KiB\n', '')
        res_mem = list(filter(lambda l: l.__contains__('Resident memory used'), lines))[0].split(' : ')[1].replace(
            ' KiB\n', '')
        perf_data.append((i, int(runs), int(states), int(time), int(virt_mem), int(res_mem)))

f = open(upp_mgr.UPPAAL_OUT_PATH.format(SCENARIO + 'performance_data').replace('.txt', '.csv'), 'w')

writer = csv.writer(f)

for row in perf_data:
    writer.writerow(row)

f.close()

perf_data.sort(key=lambda tup: tup[1])

plt.figure()

plt.plot([tup[1] for tup in perf_data], [tup[2] for tup in perf_data])
plt.title('States explored per N. Runs')

plt.show()

plt.figure()

plt.plot([tup[1] for tup in perf_data], [tup[3] / 1000 / 60 for tup in perf_data])
plt.title('Verification Time [min] per N. Runs')

plt.show()

plt.figure()

plt.plot([tup[1] for tup in perf_data], [tup[4] for tup in perf_data])
plt.title('Virtual Memory Usage [KiB] per N. Runs')

plt.show()


class Configuration:
    def __init__(self, pfw: FreeWill_Profile, pftg: Fatigue_Profile, start: Point,
                 v: float, chg: float, lb: float = None, ub: float = None):
        self.pfw = pfw
        self.pftg = pftg
        self.start = start
        self.v = v
        self.chg = chg
        self.lb = lb
        self.ub = ub

    def __eq__(self, other):
        return self.pfw == other.pfw and self.pftg == other.pftg and self.start == other.start \
               and self.v == other.v and self.chg == other.chg

    def __len__(self):
        return 8

    def __getitem__(self, item):
        if item == 0:
            return self.pfw
        elif item == 1:
            return self.pftg
        elif item == 2:
            return self.start
        elif item == 3:
            return self.v
        elif item == 4:
            return self.chg
        elif item == 6:
            return self.lb
        elif item == 7:
            return self.ub

    @staticmethod
    def parse(fields):
        lb = None
        ub = None
        if len(fields[6]) > 0:
            lb = float(fields[6])
        if len(fields[7]) > 0:
            ub = float(fields[7])

        ftg_prof = fields[1] + '/' + fields[2]

        return Configuration(FreeWill_Profile.parse_fw_profile(fields[0]), Fatigue_Profile.parse_ftg_profile(ftg_prof),
                             Point.parse(fields[3]), float(fields[4]), float(fields[5]), lb, ub)


configurations: List[Configuration] = []

with open(CSV_FILE) as csv_in:
    read = csv.reader(csv_in)
    for i, row in enumerate(read):
        if i == 0:
            continue
        else:
            configurations.append(Configuration.parse(row))

configurations = [conf for conf in configurations if conf.lb is not None and conf.ub is not None]

plt.figure(figsize=(10, 5))
fw_prof = list(set(conf.pfw for conf in configurations))
fw_values = [[conf.lb + (conf.ub - conf.lb) / 2 for conf in configurations if conf.pfw == pf] for pf in fw_prof]
plt.violinplot(fw_values, showmeans=True, positions=[i + 1 for i, x in enumerate(fw_prof)])
plt.xticks(ticks=[i + 1 for i, x in enumerate(fw_prof)], labels=fw_prof)
plt.show()

plt.figure(figsize=(10, 5))
age_group = list(set(str(conf.pftg).split('/')[0] for conf in configurations))
ftg_values = [[conf.lb + (conf.ub - conf.lb) / 2 for conf in configurations if str(conf.pftg).split('/')[0] == pf] for
              pf in age_group]
plt.violinplot(ftg_values, showmeans=True, positions=[i + 1 for i, x in enumerate(age_group)])
plt.xticks(ticks=[i + 1 for i, x in enumerate(age_group)], labels=age_group)
plt.show()

plt.figure(figsize=(10, 5))
health_stat = list(set(str(conf.pftg).split('/')[1] for conf in configurations))
ftg_values = [[conf.lb + (conf.ub - conf.lb) / 2 for conf in configurations if str(conf.pftg).split('/')[1] == pf] for
              pf in health_stat]
plt.violinplot(ftg_values, showmeans=True, positions=[i + 1 for i, x in enumerate(health_stat)])
plt.xticks(ticks=[i + 1 for i, x in enumerate(health_stat)], labels=health_stat)
plt.show()

plt.figure(figsize=(20, 5))
start_pos = list(set(conf.start for conf in configurations))
start_values = [[conf.lb + (conf.ub - conf.lb) / 2 for conf in configurations if conf.start == pf] for pf in start_pos]
plt.violinplot(start_values, showmeans=True, positions=[i + 1 for i, x in enumerate(start_pos)])
plt.xticks(ticks=[i + 1 for i, x in enumerate(start_pos)], labels=[str(x) for x in start_pos])
plt.show()

plt.figure(figsize=(20, 5))
rob_chg = [(conf.chg, conf.lb + (conf.ub - conf.lb) / 2) for conf in configurations]


def get_key(tup):
    return tup[0]


rob_chg.sort(key=get_key)
plt.plot([tup[0] for tup in rob_chg], [tup[1] for tup in rob_chg])
plt.show()

plt.figure(figsize=(20, 5))
rob_speed = [(conf.v, conf.lb + (conf.ub - conf.lb) / 2) for conf in configurations]
rob_speed.sort(key=get_key)
plt.plot([tup[0] for tup in rob_speed], [tup[1] for tup in rob_speed])
plt.show()
