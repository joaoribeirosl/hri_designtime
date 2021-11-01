import configparser
from typing import List
from src.logging.logger import Logger
import json
from src.domain.hri_const import Constants as const
from src.domain.human import Human, Interaction_Pattern, Fatigue_Profile, FreeWill_Profile
from src.domain.robot import Robot
from src.logging.logger import Logger
from src.domain.layout import Layout, Point

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


class Json_Mgr:
    JSON_PATH = config['PARAMS SETTINGS']['PARAMS_PATH']
    JSON_EXT = config['PARAMS SETTINGS']['PARAMS_EXT']
    SCENARIO_NAME = config['PARAMS SETTINGS']['SCENARIO_NAME']
    PARAMS_FILE = config['PARAMS SETTINGS']['PARAMS_FILE']

    def __init__(self):
        self.LOGGER = Logger('Json_Mgr')
        self.hums: List[Human] = []
        self.robots: List[Robot] = []
        self.layout: Layout = Layout([], [])

    def load_json(self):
        with open(self.JSON_PATH + self.PARAMS_FILE + self.JSON_EXT, 'r') as json_file:
            data = json.load(json_file)
            # parse humans
            humans_data = data['humans']
            for h in humans_data:
                self.hums.append(Human(h['name'], h['h_id'], h['v'], Interaction_Pattern.parse_ptrn(h['ptrn']),
                                       Fatigue_Profile.parse_ftg_profile(h['p_f']),
                                       FreeWill_Profile.parse_fw_profile(h['p_fw']),
                                       Point(h['start'][0], h['start'][1]), Point(h['dest'][0], h['dest'][1]),
                                       h['dext']))
            # parse robots
            robots_data = data['robots']
            for r in robots_data:
                self.robots.append(
                    Robot(r['name'], r['r_id'], r['v'], r['a'], Point(r['start'][0], r['start'][1]), r['chg']))
