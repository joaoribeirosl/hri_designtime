import configparser

from src.logging.logger import Logger
from src.mgr.json_mgr import Json_Mgr
from src.mgr.param_mgr import Param_Mgr
from src.mgr.tplt_mgr import Template_Mgr

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()

LOGGER = Logger('main')

LOGGER.info('Starting configuration of HRI scenario...')

SCENARIO_NAME = config['PARAMS SETTINGS']['SCENARIO_NAME']

json_mgr = Json_Mgr()
json_mgr.load_json()

# TODO: Replaces PARAM keywords within main template file with scenario parameters
param_mgr = Param_Mgr(json_mgr.hums, json_mgr.robots, json_mgr.layout)

# Replaces TPLT keywords within main template file with individual automata templates
tplt_mgr = Template_Mgr()
tplt_mgr.replace_tplt(SCENARIO_NAME)

# TODO: Run Uppaal Experiment
