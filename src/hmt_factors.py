import csv
import json
import sys
from typing import List

from src.domain.hmtfactor import Configuration
from src.domain.query import Query, Query_Type
from src.logging.logger import Logger
from src.mgr.factor_mgr import Factor_Mgr
from src.mgr.json_mgr import Json_Mgr
from src.mgr.param_mgr import Param_Mgr
from src.mgr.query_mgr import Query_Mgr
from src.mgr.tplt_mgr import Template_Mgr
from src.mgr.upp_mgr import Upp_Mgr


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

with open(CONFIG_JSON_PATH) as json_file:
    data = json.load(json_file)
    N_CONFIG = int(data['N_CONFIG'])
    N = int(data['N_BOUND'])
    N_SIM = int(data['N_SIM'])
    N_SAMPLE = int(data['N_SAMPLE'])
    filter_processed = data['filter_processed'] == 'true'
    resample = data['resample'] == 'true'
    sample_sim = data['sample_sim'] == 'true'

LOGGER = Logger('EASE MAIN')

LOGGER.info('Reading scenario template...')

json_mgr = Json_Mgr()
json_mgr.load_json()

upp_mgr = Upp_Mgr()

CSV_FILE = upp_mgr.UPPAAL_OUT_PATH.format(SCENARIO).replace('.txt', '.csv')

SIM_PATH = upp_mgr.UPPAAL_OUT_PATH.replace('/{}.txt', '')

configurations: List[Configuration] = []

factor_mgr = Factor_Mgr(json_mgr)

if resample:
    f = open(CSV_FILE, 'w')
    f.truncate(0)
    f.close()

    for i in range(N_CONFIG):
        new_conf = Configuration.sample(CONFIG_JSON_PATH)
        while not factor_mgr.validate(new_conf):
            new_conf = Configuration.sample(CONFIG_JSON_PATH)
        configurations.append(new_conf)
        if sample_sim:
            sim_files = []
            for j in range(N_SIM):
                factor_mgr.apply(new_conf)
                sim_param_mgr = Param_Mgr(json_mgr.hums, json_mgr.robots, json_mgr.layout, json_mgr.params)
                sim_param_mgr.replace_params(SCENARIO)
                sim_tplt_mgr = Template_Mgr(sim_param_mgr)
                sim_tplt_mgr.replace_tplt(SCENARIO)
                factor_mgr.fix_orch_params(new_conf, SCENARIO)

                tau_i = [i for i, f in enumerate(new_conf.factors) if 'TAU' in f.hmt_id][0]

                sim_query_mgr = Query_Mgr([Query(Query_Type.SIM, new_conf.factors[tau_i].value, 1,
                                                 json_mgr.hums, json_mgr.robots)])
                sim_query_mgr.gen_q_file(SCENARIO)

                out_file = upp_mgr.run_exp(SCENARIO)
                sim_files.append(out_file)

            for sim in sim_files:
                configurations.extend(Configuration.parse_from_sim(CONFIG_JSON_PATH, N_SAMPLE,
                                                                   sim, new_conf.factors[tau_i].value))
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

N = N if N >= 0 else len(configurations)

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

    if conf.get_checkpoint() == len(json_mgr.hums):
        LOGGER.warn('Discarding configuration (empty mission).')
        continue

    # Replaces PARAM keywords within main template file with scenario parameters
    param_mgr = Param_Mgr(json_mgr.rescale_hums(conf.get_checkpoint()), json_mgr.robots, json_mgr.layout, json_mgr.params)
    param_mgr.replace_params(SCENARIO_NAME)

    # Replaces TPLT keywords within main template file with individual automata templates
    tplt_mgr = Template_Mgr(param_mgr)
    tplt_mgr.replace_tplt(SCENARIO_NAME)

    factor_mgr.fix_orch_params(conf, SCENARIO_NAME)

    # Generate query file
    query_mg = Query_Mgr(json_mgr.queries)
    query_mg.hums = json_mgr.rescale_hums(conf.get_checkpoint())
    query_mg.gen_q_file(SCENARIO_NAME)

    # Run Uppaal Experiment
    out_file = upp_mgr.run_exp(SCENARIO_NAME)

    try:
        factor_mgr.save_metrics(conf, out_file)
    except IndexError:
        LOGGER.error('Verification unsuccessful.')

    update_csv(configurations)

LOGGER.info('Done.')
