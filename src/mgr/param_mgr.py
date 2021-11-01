import configparser

from src.domain.hri_const import Constants as const
from src.logging.logger import Logger

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


class Param_Mgr:



    def __init__(self):
        self.LOGGER = Logger('Param_Mgr')
