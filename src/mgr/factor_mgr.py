from typing import List, Tuple

from src.domain.hmtfactor import Configuration, HMTFactor, Metric
from src.domain.query import Query
from src.logging.logger import Logger
from src.mgr.json_mgr import Json_Mgr


class Factor_Mgr:
    def __init__(self, scenario: Json_Mgr):
        self.LOGGER = Logger('Factor_Mgr')
        self.scenario = scenario

    def get_agent_list(self, s: str):
        agent_category = s.split('_')[0]
        if agent_category == 'HUM':
            return self.scenario.hums
        elif agent_category == 'ROB':
            return self.scenario.robots

    def get_agents(self, s: str):
        agent_id = int(s.split('_')[1])
        if s.split('_')[0] == 'ROB':
            return [self.get_agent_list(s)[agent_id - 1]]
        else:
            return [agent for agent in self.get_agent_list(s) if agent_id in [agent.h_id, agent.same_as]]

    def set_factor_value(self, factor: HMTFactor):
        factor_name = factor.hmt_id.split('_')[2]
        if factor_name == 'FW':
            for h in self.get_agents(factor.hmt_id):
                h.p_fw = factor.value
        elif factor_name == 'FTG':
            for h in self.get_agents(factor.hmt_id):
                h.p_f = factor.value
        elif factor_name == 'CHG':
            for r in self.get_agents(factor.hmt_id):
                r.chg = factor.value
        elif factor_name == 'POS':
            self.get_agents(factor.hmt_id)[0].start = factor.value
        elif factor_name == 'VEL':
            for a in self.get_agents(factor.hmt_id):
                a.v = factor.value
                if factor.hmt_id.split('_')[0] == 'ROB':
                    a.a = factor.value

    def apply(self, conf: Configuration):
        for factor in conf.factors:
            self.set_factor_value(factor)

    def filter_queries(self, to_process: List[str], all_queries: List[Query]):
        filtered_queries: List[Query] = []
        for q in all_queries:
            if (q.t.value == 'pscs' and 'PRSCS' in to_process) or (q.t.value == 'eftg' and 'FTG' in to_process):
                filtered_queries.append(q)
        self.scenario.queries = filtered_queries

    def parse_upp_results(self, m: Metric, out_file: str):
        with open(out_file) as upp_res:
            lines = upp_res.readlines()
            if m.m_id in ['PRSCS_LOWER_BOUND', 'PRSCS_UPPER_BOUND']:
                pr_range = \
                    [line.split(' Pr(<> ...) in ')[1].replace('[', '').replace(']', '').replace('\n', '').split(',')
                     for line in lines if line.__contains__('Pr(<> ...)')][0]
                if m.m_id == 'PRSCS_LOWER_BOUND':
                    m.value = float(pr_range[0])
                else:
                    m.value = float(pr_range[1])
            elif m.m_id.startswith('FTG'):
                ftg_ranges = [line.split('Values in [')[1].split(']')[0].split(',')
                              for line in lines if line.__contains__('Values in ')]
                ftg_ranges = [(float(r[0]), float(r[1])) for r in ftg_ranges]
                ftg_ranges = [(r[0] + (r[1] - r[0]) / 2, (r[1] - r[0]) / 2) for r in ftg_ranges]
                h_ids = [h.h_id - 1 for h in self.get_agents(m.m_id.replace('FTG_', ''))]
                ftg_range: Tuple[float, float] = tuple()
                for r_i, r in enumerate(ftg_ranges):
                    if r_i not in h_ids:
                        continue
                    if len(ftg_range) == 0 or r[0] > ftg_range[0]:
                        ftg_range = (r[0], r[1])
                m.value = '{:.4f}+-{:.4f}'.format(ftg_range[0], ftg_range[1])

    def save_metrics(self, conf: Configuration, out_file: str):
        for m in conf.metrics:
            self.parse_upp_results(m, out_file)
