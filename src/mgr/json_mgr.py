import configparser
import json
import sys
from typing import List, Dict

from src.domain.human import Human, Interaction_Pattern, Fatigue_Profile, FreeWill_Profile
from src.domain.layout import Layout, Point, Area
from src.domain.query import Query, Query_Type
from src.domain.robot import Robot
from src.logging.logger import Logger

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


class Json_Mgr:
    JSON_PATH = config['PARAMS SETTINGS']['PARAMS_PATH']
    JSON_EXT = config['PARAMS SETTINGS']['PARAMS_EXT']
    SCENARIO_NAME = sys.argv[1] if len(sys.argv) >= 2 else None
    PARAMS_FILE = sys.argv[1] if len(sys.argv) >= 2 else None

    def __init__(self):
        self.LOGGER = Logger('Json_Mgr')
        self.hums: List[Human] = []
        self.robots: List[Robot] = []
        self.layout: Layout = Layout([], [], 0)
        self.queries: List[Query] = []
        self.params: Dict[str, str] = dict()

    def load_json(self):
        with open(self.JSON_PATH + self.PARAMS_FILE + self.JSON_EXT, 'r') as json_file:
            data = json.load(json_file)
            # parse global params
            try:
                for d in data['global_params']:
                    self.params.update(d)
            except KeyError:
                self.LOGGER.warn("No global params specified.")
                self.params['behavioral_model'] = 'random'
            # parse humans
            humans_data = data['humans']
            self.LOGGER.info("Loading human-related data...")
            for h in humans_data:
                self.hums.append(Human(h['name'], h['h_id'], h['v'], Interaction_Pattern.parse_ptrn(h['ptrn']),
                                       Fatigue_Profile.parse_ftg_profile(h['p_f']),
                                       FreeWill_Profile.parse_fw_profile(h['p_fw']),
                                       Point(h['start'][0], h['start'][1]), Point(h['dest'][0], h['dest'][1]),
                                       h['dext'], h['same_as'], h['path'], self.params['behavioral_model']))
            self.LOGGER.info("Successfully loaded.")
            # parse robots
            robots_data = data['robots']
            self.LOGGER.info("Loading robot-related data...")
            for r in robots_data:
                self.robots.append(
                    Robot(r['name'], r['r_id'], r['v'], r['a'], Point(r['start'][0], r['start'][1]), r['chg']))
            self.LOGGER.info("Successfully loaded.")
            # parse layout
            areas_data = data['areas']
            inters_pts_data = data['intersect']
            self.LOGGER.info("Loading layout-related data...")
            for a in areas_data:
                self.layout.areas.append(
                    Area(Point(a['p1'][0], a['p1'][1]), Point(a['p2'][0], a['p2'][1]), Point(a['p3'][0], a['p3'][1]),
                         Point(a['p4'][0], a['p4'][1])))
            for pt in inters_pts_data:
                self.layout.inter_pts.append(Point(pt['p'][0], pt['p'][1]))
            self.layout.max_neigh = data['max_neigh']
            self.LOGGER.info("Successfully loaded.")
            # parse queries
            queries_data = data['queries']
            self.LOGGER.info("Loading query-related data...")
            for q in queries_data:
                self.queries.append(Query(Query_Type.parse_query(q['type']), q['tau'], q['n'], self.hums, self.robots))
            self.LOGGER.info("Successfully loaded.")
