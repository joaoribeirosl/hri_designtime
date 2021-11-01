import configparser
from typing import List

from src.domain.hri_const import Constants as const
from src.domain.human import Human
from src.domain.robot import Robot
from src.logging.logger import Logger

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


class Param_Mgr:
    TPLT_PATH = config['TEMPLATES SETTING']['TEMPLATES_PATH']
    DEST_PATH = config['TEMPLATES SETTING']['MODEL_PATH']
    TPLT_EXT = config['TEMPLATES SETTING']['TEMPLATES_EXT']
    MAIN = const.MAIN_TPLT.value

    HUM_KEYWORDS = [const.N_H.value, const.N_H_bool.value, const.N_H_double.value, const.N_H_int.value,
                    const.PATTERNS.value, const.DEST_X.value, const.DEST_Y.value]
    LAYOUT_KEYWORDS = [const.N_AREAS.value, const.N_POINTS.value, const.N_INTERSECT.value, const.LAYOUT.value,
                       const.INTERSECT.value]
    INST_KEYWORDS = [const.ROB_INST.value, const.ORCH_INST.value, const.HUM_INST.value, const.ALL_INST.value]

    def __init__(self, hums: List[Human], robs: List[Robot]):
        self.LOGGER = Logger('Param_Mgr')
        self.hums = hums
        self.robs = robs
