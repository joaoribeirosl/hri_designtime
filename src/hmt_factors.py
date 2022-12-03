import itertools
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

FILE_PATH = '/Users/lestingi/PycharmProjects/hri_designtime/resources/input_params/ease_exp/DPa.json'
NAME = 'DPa_{}'

LOGGER = Logger('EASE MAIN')

LOGGER.info('Reading scenario template...')

json_mgr = Json_Mgr()
json_mgr.load_json()

# free will
fw_values = [FreeWill_Profile.FOCUSED, FreeWill_Profile.FREE, FreeWill_Profile.DISTRACTED]

# fatigue profile
ftg_values = [Fatigue_Profile.YOUNG_HEALTHY, Fatigue_Profile.YOUNG_SICK,
              Fatigue_Profile.ELDERLY_HEALTHY, Fatigue_Profile.ELDERLY_SICK, Fatigue_Profile.COVID_PATIENT]

# starting position
start_values: List[Point] = []
ETA = 5.0
DELTA = 2000.0
for area in json_mgr.layout.areas:
    x_s = np.arange(area.corners[0].x + ETA, area.corners[2].x - ETA, DELTA)
    y_s = np.arange(area.corners[0].y + ETA, area.corners[2].y - ETA, DELTA)
    start_values.extend([Point(x, y) for x in x_s for y in y_s])

# robot speed
speed_values = [26.0, 83.0, 100.0]

# robot charge
charge_values = np.arange(11.2, 12.4, 0.2)

factors = [fw_values, ftg_values, start_values, speed_values, charge_values]

for i, configuration in enumerate(list(itertools.product(*factors))[:3]):
    LOGGER.info('Processing configuration {}...'.format(i))

    SCENARIO_NAME = NAME.format(i)

    json_mgr.hums[0].p_fw = configuration[0]
    json_mgr.hums[3].p_fw = configuration[0]
    json_mgr.hums[4].p_fw = configuration[0]
    json_mgr.hums[0].p_f = configuration[1]
    json_mgr.hums[3].p_f = configuration[1]
    json_mgr.hums[4].p_f = configuration[1]
    json_mgr.hums[1].start = configuration[2]
    json_mgr.robots[0].v = configuration[3]
    json_mgr.robots[0].a = configuration[3]
    json_mgr.robots[0].chg = configuration[4]

    # Replaces PARAM keywords within main template file with scenario parameters
    param_mgr = Param_Mgr(json_mgr.hums, json_mgr.robots, json_mgr.layout)
    param_mgr.replace_params(SCENARIO_NAME)

    # Replaces TPLT keywords within main template file with individual automata templates
    tplt_mgr = Template_Mgr(param_mgr)
    tplt_mgr.replace_tplt(SCENARIO_NAME)

    # Generate query file
    query_mg = Query_Mgr(json_mgr.queries)
    query_mg.gen_q_file(SCENARIO_NAME)

    # Run Uppaal Experiment
    upp_mgr = Upp_Mgr()
    upp_mgr.run_exp(SCENARIO_NAME)

LOGGER.info('Done.')
