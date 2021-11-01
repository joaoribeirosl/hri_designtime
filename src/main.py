from src.logging.logger import Logger
from src.mgr.tplt_mgr import Template_Mgr

LOGGER = Logger('main')

LOGGER.info('Starting configuration of HRI scenario...')

# FIXME: should be passed as inputs
SCENARIO_NAME = 'test1'
PARAMS_FILE = 'test1'

tplt_mgr = Template_Mgr()
# TODO: Replaces PARAM keywords within main template file with scenario parameters

# Replaces TPLT keywords within main template file with individual automata templates
tplt_mgr.replace_tplt(SCENARIO_NAME)

# TODO: Run Uppaal Experiment

