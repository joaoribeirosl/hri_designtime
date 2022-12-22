import csv
import random
import sys
from typing import List

import numpy as np

from src.domain.human import Fatigue_Profile, FreeWill_Profile
from src.domain.layout import Point
from src.logging.logger import Logger
from src.mgr.json_mgr import Json_Mgr
from src.mgr.param_mgr import Param_Mgr
from src.mgr.query_mgr import Query_Mgr
from src.mgr.tplt_mgr import Template_Mgr
from src.mgr.upp_mgr import Upp_Mgr


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
        if len(fields[5]) > 0:
            lb = float(fields[5])
        if len(fields[6]) > 0:
            ub = float(fields[6])

        return Configuration(FreeWill_Profile.parse_fw_profile(fields[0]), Fatigue_Profile.parse_ftg_profile(fields[1]),
                             Point.parse(fields[2]), float(fields[3]), float(fields[4]), lb, ub)


def update_csv():
    with open(CSV_FILE, 'w') as out_csv:
        write = csv.writer(out_csv)
        write.writerow(HEADER)
        for conf_towrite in configurations:
            write.writerow([conf_towrite.pfw, conf_towrite.pftg, conf_towrite.start,
                            conf_towrite.v, conf_towrite.chg, conf_towrite.lb, conf_towrite.ub])


SCENARIO = sys.argv[1]
FILE_PATH = '/home/lestingi/designtime/hri_designtime/resources/input_params/{}.json'.format(SCENARIO)

LOGGER = Logger('EASE MAIN')

LOGGER.info('Reading scenario template...')

json_mgr = Json_Mgr()
json_mgr.load_json()

upp_mgr = Upp_Mgr()
query_mg = Query_Mgr(json_mgr.queries)

CSV_FILE = upp_mgr.UPPAAL_OUT_PATH.format(SCENARIO).replace('.txt', '.csv')
HEADER = ['PATIENT_FREEWILL', 'PATIENT_FATIGUE', 'DOCTOR_START',
          'ROBOT_SPEED', 'ROBOT_CHARGE', 'PR.SCS_LOWER_BOUND', 'PR.SCS_UPPER_BOUND']

# configurations: List[Tuple] = list(itertools.product(*factors))
configurations: List[Configuration] = []

resample = False

if resample:
    # free will
    fw_values = [FreeWill_Profile.FOCUSED, FreeWill_Profile.FREE, FreeWill_Profile.DISTRACTED]

    # fatigue profile
    ftg_values = [Fatigue_Profile.YOUNG_HEALTHY, Fatigue_Profile.YOUNG_SICK,
                  Fatigue_Profile.ELDERLY_HEALTHY, Fatigue_Profile.ELDERLY_SICK, Fatigue_Profile.COVID_PATIENT]

    # starting position
    start_values: List[Point] = json_mgr.layout.inter_pts
    # ETA = 5.0
    # DELTA = 3000.0
    # for area in json_mgr.layout.areas:
    #    x_s = np.arange(area.corners[0].x + ETA, area.corners[2].x - ETA, DELTA)
    #    y_s = np.arange(area.corners[0].y + ETA, area.corners[2].y - ETA, DELTA)
    #    start_values.extend([Point(x, y) for x in x_s for y in y_s])

    # robot speed
    speed_values = [30.0, 100.0]

    # robot charge
    charge_values = [11.1, 12.4]

    N_SAMPLE = 1000

    # factors = [fw_values, ftg_values, start_values, speed_values, charge_values]

    for i in range(N_SAMPLE):
        pfw = random.choice(fw_values)
        pftg = random.choice(ftg_values)
        start = random.choice(start_values)
        v = speed_values[0] + ((speed_values[1] - speed_values[0]) * np.random.rand(1)[0])
        chg = charge_values[0] + ((charge_values[1] - charge_values[0]) * np.random.rand(1)[0])
        configurations.append(Configuration(pfw, pftg, start, v, chg))
else:
    with open(CSV_FILE, 'r') as csv_in:
        read = csv.reader(csv_in)
        for i, row in enumerate(read):
            if i == 0:
                continue
            else:
                configurations.append(Configuration.parse(row))
                # read_conf: Configuration = Configuration.parse(row)
                # if read_conf.lb is not None and read_conf.ub is not None:
                #    index: int = configurations.index(read_conf)
                #    configurations[index].lb = read_conf.lb
                #    configurations[index].ub = read_conf.ub

LOGGER.info('{} Configurations to process.'.format(len(configurations)))

if len(sys.argv) > 2:
    N = int(sys.argv[2])
else:
    N = len(configurations)

if len(sys.argv) > 3:
    filter_processed = bool(sys.argv[3])
else:
    filter_processed = False

for i, conf in enumerate(configurations[:N]):

    if filter_processed and conf.lb is not None and conf.ub is not None:
        LOGGER.info('Configuration {} already processed'.format(i))
        continue

    LOGGER.info('Processing conf {}...'.format(i))

    SCENARIO_NAME = '{}_{}'.format(SCENARIO, i)

    json_mgr.hums[0].p_fw = conf.pfw
    json_mgr.hums[3].p_fw = conf.pfw
    json_mgr.hums[4].p_fw = conf.pfw
    json_mgr.hums[0].p_f = conf.pftg
    json_mgr.hums[3].p_f = conf.pftg
    json_mgr.hums[4].p_f = conf.pftg
    json_mgr.hums[1].start = conf.start
    json_mgr.hums[0].v = conf.v
    json_mgr.hums[3].v = conf.v
    json_mgr.hums[4].v = conf.v
    json_mgr.robots[0].v = conf.v
    json_mgr.robots[0].a = conf.v
    json_mgr.robots[0].chg = conf.chg

    # Replaces PARAM keywords within main template file with scenario parameters
    param_mgr = Param_Mgr(json_mgr.hums, json_mgr.robots, json_mgr.layout)
    param_mgr.replace_params(SCENARIO_NAME)

    # Replaces TPLT keywords within main template file with individual automata templates
    tplt_mgr = Template_Mgr(param_mgr)
    tplt_mgr.replace_tplt(SCENARIO_NAME)

    # Generate query file
    query_mg.gen_q_file(SCENARIO_NAME)

    # Run Uppaal Experiment
    out_file = upp_mgr.run_exp(SCENARIO_NAME)

    try:
        with open(out_file) as upp_res:
            lines = upp_res.readlines()
            pr_range = [line.split(' Pr(<> ...) in ')[1].replace('[', '').replace(']', '').replace('\n', '').split(',')
                        for line in lines if line.__contains__('Pr(<> ...)')][0]
            configurations[i].lb = float(pr_range[0])
            configurations[i].ub = float(pr_range[1])
    except IndexError:
        LOGGER.error('Verification unsuccessful.')

    update_csv()

LOGGER.info('Done.')
