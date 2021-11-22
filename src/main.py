import configparser
import sys

from src.logging.logger import Logger
from src.mgr.json_mgr import Json_Mgr
from src.mgr.param_mgr import Param_Mgr
from src.mgr.query_mgr import Query_Mgr
from src.mgr.tplt_mgr import Template_Mgr
from src.mgr.upp_mgr import Upp_Mgr

config = configparser.ConfigParser()
config.read(sys.argv[1])
config.sections()

LOGGER = Logger('main')

LOGGER.info('Starting configuration of HRI scenario...')

SCENARIO_NAME = config['PARAMS SETTINGS']['SCENARIO_NAME']

json_mgr = Json_Mgr()
json_mgr.load_json()

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
