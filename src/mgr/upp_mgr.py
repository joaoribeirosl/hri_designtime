import configparser
import os
from src.logging.logger import Logger

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


class Upp_Mgr:
    SCRIPT_PATH = config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH']
    UPPAAL_PATH = config['UPPAAL SETTINGS']['UPPAAL_PATH']
    UPPAAL_XML_PATH = config['TEMPLATES SETTING']['MODEL_PATH']
    MODEL_EXT = config['TEMPLATES SETTING']['TEMPLATES_EXT']
    UPPAAL_Q_PATH = config['TEMPLATES SETTING']['QUERY_PATH']
    QUERY_EXT = config['TEMPLATES SETTING']['QUERY_EXT']
    UPPAAL_OUT_PATH = config['UPPAAL SETTINGS']['UPPAAL_OUT_PATH']

    def __init__(self):
        self.LOGGER = Logger('Uppaal_Mgr')

    def run_exp(self, scen_name):
        self.LOGGER.info('Starting verification...')
        os.system('{} {} {} {} {}'.format(self.SCRIPT_PATH, self.UPPAAL_PATH,
                                          self.UPPAAL_XML_PATH + scen_name + self.MODEL_EXT,
                                          self.UPPAAL_XML_PATH + scen_name + self.QUERY_EXT,
                                          self.UPPAAL_OUT_PATH.format(scen_name)))
        self.LOGGER.info('Verification complete.')
