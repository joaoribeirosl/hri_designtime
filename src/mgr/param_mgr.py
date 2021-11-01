import configparser
from typing import List

from src.domain.hri_const import Constants as const
from src.domain.human import Human
from src.domain.robot import Robot
from src.logging.logger import Logger
from src.domain.layout import Layout

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

    def __init__(self, hums: List[Human], robs: List[Robot], layout: Layout):
        self.LOGGER = Logger('Param_Mgr')
        self.hums = hums
        self.N_H = len(hums)
        self.robs = robs
        self.layout = layout
        self.N_A = len(layout.areas)
        self.N_I = len(layout.inter_pts)
        self.N_P = self.N_I - 1

    def replace_hum_keys(self, scen_name):
        with open(self.TPLT_PATH + self.MAIN + self.TPLT_EXT, 'r') as main_tplt:
            self.LOGGER.debug('Replacing Human-related parameters...')
            main_content = main_tplt.read()
            for key in self.HUM_KEYWORDS:
                value = None
                if key == const.N_H.value:
                    value = str(self.N_H) + ";\n"
                elif key == const.N_H_bool.value:
                    value = "{" + "false, " * (self.N_H - 1) + "false};\n"
                elif key == const.N_H_double.value:
                    value = "{" + "0.0, " * (self.N_H - 1) + "0.0};\n"
                elif key == const.N_H_int.value:
                    value = "{" + "0, " * (self.N_H - 1) + "0};\n"
                elif key == const.PATTERNS.value:
                    value = "{" + ''.join([str(h.ptrn.to_int()) + "," for h in self.hums[:self.N_H - 1]]) + \
                            str(self.hums[-1].ptrn.to_int()) + "};\n"
                elif key == const.DEST_X.value:
                    value = "{" + ''.join([str(h.dest.x) + "," for h in self.hums[:self.N_H - 1]]) + \
                            str(self.hums[-1].dest.x) + "};\n"
                elif key == const.DEST_Y.value:
                    value = "{" + ''.join([str(h.dest.y) + "," for h in self.hums[:self.N_H - 1]]) + \
                            str(self.hums[-1].dest.y) + "};\n"
                main_content = main_content.replace(key, str(value))
            dest_model = open(self.DEST_PATH + scen_name + self.TPLT_EXT, 'w')
            dest_model.write(main_content)
            dest_model.close()
            self.LOGGER.info('{} model successfully saved in {}.'.format(scen_name, self.DEST_PATH))

    def replace_layout_keys(self, scen_name):
        with open(self.DEST_PATH + scen_name + self.TPLT_EXT, 'r') as main_tplt:
            self.LOGGER.debug('Replacing Layout-related parameters...')
            main_content = main_tplt.read()
            for key in self.LAYOUT_KEYWORDS:
                value = None
                if key == const.N_AREAS.value:
                    value = str(self.N_A) + ';\n'
                elif key == const.N_POINTS.value:
                    value = str(self.N_P) + ';\n'
                elif key == const.N_INTERSECT.value:
                    value = str(self.N_I) + ';\n'
                elif key == const.LAYOUT.value:
                    value = '{'
                    for (i, a) in enumerate(self.layout.areas):
                        value += '{'
                        for (j, p) in enumerate(a.corners):
                            value += '{' + str(p.x) + ', ' + str(p.y) + '}'
                            if j <= 2:
                                value += ','
                        value += '}'
                        if i <= self.N_A - 2:
                            value += ','
                    value += '};\n'
                elif key == const.INTERSECT.value:
                    value = '{'
                    for (i, pt) in enumerate(self.layout.inter_pts):
                        value += '{' + str(pt.x) + ', ' + str(pt.y) + '}'
                        if i <= self.N_I - 2:
                            value += ','
                    value += '};\n'
                main_content = main_content.replace(key, str(value))
        dest_model = open(self.DEST_PATH + scen_name + self.TPLT_EXT, 'w')
        dest_model.write(main_content)
        dest_model.close()
        self.LOGGER.info('{} model successfully saved in {}.'.format(scen_name, self.DEST_PATH))

    def replace_params(self, scen_name):
        self.replace_hum_keys(scen_name)
        self.replace_layout_keys(scen_name)
