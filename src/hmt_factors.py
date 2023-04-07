import csv
import sys
from typing import List

from src.domain.hmtfactor import Configuration
from src.logging.logger import Logger
from src.mgr.json_mgr import Json_Mgr
from src.mgr.param_mgr import Param_Mgr
from src.mgr.query_mgr import Query_Mgr
from src.mgr.tplt_mgr import Template_Mgr
from src.mgr.upp_mgr import Upp_Mgr
from src.mgr.factor_mgr import Factor_Mgr


def update_csv(configurations: List[Configuration]):
    with open(CSV_FILE, 'w') as out_csv:
        write = csv.writer(out_csv)
        write.writerow(configurations[0].get_header())
        for conf_towrite in configurations:
            write.writerow([f.value for f in conf_towrite.factors] + [m.value for m in conf_towrite.metrics])


SCENARIO = sys.argv[1]
FILE_PATH = './resources/input_params/ease_exp/{}.json'.format(SCENARIO)

CONFIG_JSON = sys.argv[2]
CONFIG_JSON_PATH = './resources/config/{}.json'.format(CONFIG_JSON)

LOGGER = Logger('EASE MAIN')

LOGGER.info('Reading scenario template...')

json_mgr = Json_Mgr()
json_mgr.load_json()

upp_mgr = Upp_Mgr()

CSV_FILE = upp_mgr.UPPAAL_OUT_PATH.format(SCENARIO).replace('.txt', '.csv')

configurations: List[Configuration] = []

resample = len(sys.argv) > 5

factor_mgr = Factor_Mgr(json_mgr)

if resample:
    f = open(CSV_FILE, 'w')
    f.truncate(0)
    f.close()
    N_SAMPLE = int(sys.argv[5])
    for i in range(N_SAMPLE):
        new_conf = Configuration.sample(CONFIG_JSON_PATH)
        while not factor_mgr.validate(new_conf):
            new_conf = Configuration.sample(CONFIG_JSON_PATH)
        configurations.append(new_conf)
    update_csv(configurations)
else:
    with open(CSV_FILE, 'r') as csv_in:
        read = csv.reader(csv_in)
        for i, row in enumerate(read):
            if i == 0:
                continue
            else:
                configurations.append(Configuration.parse(CONFIG_JSON_PATH, row))

LOGGER.info('{} Configurations to process.'.format(len(configurations)))

if len(sys.argv) > 3:
    N = int(sys.argv[3])
else:
    N = len(configurations)

if len(sys.argv) > 4:
    filter_processed = bool(sys.argv[4])
else:
    filter_processed = False

queries_copy = json_mgr.queries.copy()

for i, conf in enumerate(configurations[:N]):
    if filter_processed:
        if len(conf.processed()) == len(conf.metrics):
            LOGGER.info('Configuration {} already processed'.format(i))
            continue
        else:
            to_be_processed = [m.m_id for j, m in enumerate(conf.metrics) if j not in conf.processed()]
            LOGGER.info('Configuration {}: {} to be estimated.'.format(i, ','.join(to_be_processed)))
            to_be_processed = [x.split('_')[0] for x in to_be_processed]
            factor_mgr.filter_queries(to_be_processed, queries_copy)

    LOGGER.info('Processing conf {}...'.format(i))

    SCENARIO_NAME = '{}_{}'.format(SCENARIO, i)

    factor_mgr.apply(conf)

    # Replaces PARAM keywords within main template file with scenario parameters
    param_mgr = Param_Mgr(json_mgr.hums, json_mgr.robots, json_mgr.layout, json_mgr.params)
    param_mgr.replace_params(SCENARIO_NAME)

    # Replaces TPLT keywords within main template file with individual automata templates
    tplt_mgr = Template_Mgr(param_mgr)
    tplt_mgr.replace_tplt(SCENARIO_NAME)

    factor_mgr.fix_orch_params(conf, SCENARIO_NAME)

    # Generate query file
    query_mg = Query_Mgr(json_mgr.queries)
    query_mg.gen_q_file(SCENARIO_NAME)

    # Run Uppaal Experiment
    out_file = upp_mgr.run_exp(SCENARIO_NAME)

    try:
        factor_mgr.save_metrics(conf, out_file)
    except IndexError:
        LOGGER.error('Verification unsuccessful.')

    update_csv(configurations)

LOGGER.info('Done.')
