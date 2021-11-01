from src.logging.logger import Logger
from src.mgr.tplt_mgr import Template_Mgr

LOGGER = Logger('main')

LOGGER.info('Starting configuration of HRI scenario...')

SCENARIO_NAME = 'test1'

tplt_mgr = Template_Mgr()
tplt_mgr.replace_tplt(SCENARIO_NAME)
