import json
import random
from typing import List, Tuple, Any

import numpy as np

from src.domain.human import Fatigue_Profile, FreeWill_Profile
from src.domain.layout import Point


class HMTFactor:
    def __init__(self, hmt_id: str, hmt_type: str, ranges: List[Tuple[float, float]] = None, value: Any = None):
        self.hmt_id = hmt_id
        self.hmt_type = hmt_type
        self.ranges = ranges
        self.value = value

    def set_value(self, s: str = None):
        if s is None or len(s) == 0:
            self.value = None

        if self.hmt_type == 'float':
            self.value = float(s)
        elif self.hmt_type == 'int':
            self.value = int(s)
        elif self.hmt_type == 'str':
            self.value = s
        elif self.hmt_type == 'FreeWillProfile':
            self.value = FreeWill_Profile.parse_fw_profile(s)
        elif self.hmt_type == 'FatigueProfile':
            self.value = Fatigue_Profile.parse_ftg_profile(s)
        elif self.hmt_type == 'Point':
            self.value = Point.parse(s)

    def sample(self):
        if self.hmt_type == 'float':
            self.set_value(str(self.ranges[0][0] + ((self.ranges[0][1] - self.ranges[0][0]) * np.random.rand(1)[0])))
        elif self.hmt_type == 'int':
            self.set_value(str(random.randint(int(self.ranges[0][0]), int(self.ranges[0][1]))))
        elif self.hmt_type == 'str':
            # FIXME
            self.set_value()
        elif self.hmt_type == 'FreeWillProfile':
            fw_values = [FreeWill_Profile.FOCUSED, FreeWill_Profile.FREE, FreeWill_Profile.DISTRACTED]
            self.set_value(random.choice(fw_values).value)
        elif self.hmt_type == 'FatigueProfile':
            ftg_values = [Fatigue_Profile.YOUNG_HEALTHY, Fatigue_Profile.YOUNG_SICK,
                          Fatigue_Profile.ELDERLY_HEALTHY, Fatigue_Profile.ELDERLY_SICK,
                          Fatigue_Profile.YOUNG_UNSTEADY, Fatigue_Profile.ELDERLY_UNSTEADY]
            self.set_value(random.choice(ftg_values).value)
        elif self.hmt_type == 'Point':
            # TODO: must be within an area...
            x = self.ranges[0][0] + ((self.ranges[0][1] - self.ranges[0][0]) * np.random.rand(1)[0])
            y = self.ranges[1][0] + ((self.ranges[1][1] - self.ranges[1][0]) * np.random.rand(1)[0])
            self.set_value('{:.2f},{:.2f}'.format(x, y))


class Metric:
    def __init__(self, m_id: str, m_type: str, value: Any = None):
        self.m_id = m_id
        self.m_type = m_type
        self.value = value

    def set_value(self, s: str):
        if s is None or len(s) == 0:
            self.value = None
        elif self.m_type == 'float':
            self.value = float(s)
        elif self.m_type == 'str':
            self.value = s

    def processed(self):
        return self.value is not None


class Configuration:
    def __init__(self, factors: List[HMTFactor], metrics: List[Metric]):
        self.factors = factors
        self.metrics = metrics

    def __eq__(self, other):
        return all([f in other.factors for f in self.factors])

    def __len__(self):
        return len(self.factors) + len(self.metrics)

    def __getitem__(self, item):
        if item < len(self.factors):
            return self.factors[item].value
        else:
            return self.metrics[item - len(self.factors)].value

    def lookup(self, key: str):
        for i, factor in enumerate(self.factors):
            if factor.hmt_id == key:
                return i
        for i, metric in enumerate(self.metrics):
            if metric.m_id == key:
                return i + len(self.factors)

    def get_header(self):
        return [f.hmt_id for f in self.factors] + [m.m_id for m in self.metrics]

    def processed(self):
        return [i for i, m in enumerate(self.metrics) if m.processed()]

    @staticmethod
    def config(config_json: str):
        new_factors: List[HMTFactor] = []
        new_metrics: List[Metric] = []
        with open(config_json, 'r') as json_file:
            data = json.load(json_file)
            for f in data['factors']:
                ranges: List[Tuple[float, float]] = []
                try:
                    ranges.append((float(f["min"]), float(f["max"])))
                    new_factors.append(HMTFactor(f['id'], f['type'], ranges))
                except KeyError:
                    try:
                        ranges.append((float(f["min_x"]), float(f["max_x"])))
                        ranges.append((float(f["min_y"]), float(f["max_y"])))
                        new_factors.append(HMTFactor(f['id'], f['type'], ranges))
                    except KeyError:
                        new_factors.append(HMTFactor(f['id'], f['type']))

            for m in data['metrics']:
                new_metrics.append(Metric(m['id'], m['type']))

        return Configuration(new_factors, new_metrics)

    @staticmethod
    def sample(config_json: str):
        new_conf = Configuration.config(config_json)

        for factor in new_conf.factors:
            factor.sample()

        return new_conf

    @staticmethod
    def parse(config_json: str, fields: List[str]):
        new_conf = Configuration.config(config_json)

        for i, factor in enumerate(new_conf.factors):
            factor.set_value(fields[i])
        for i, metric in enumerate(new_conf.metrics):
            metric.set_value(fields[len(new_conf.factors) + i])

        return new_conf
