from enum import Enum

from src.domain.layout import Point


class Interaction_Pattern(Enum):
    ASSISTANT = "ASSISTANT"
    COMPETITOR = "COMPETITOR"
    FOLLOWER = "FOLLOWER"
    LEADER = "LEADER"
    RECIPIENT = "RECIPIENT"
    RESCUER = "RESCUER"

    @staticmethod
    def parse_ptrn(p: str):
        if p == "ASSISTANT":
            return Interaction_Pattern.ASSISTANT
        elif p == "COMPETITOR":
            return Interaction_Pattern.COMPETITOR
        elif p == "FOLLOWER":
            return Interaction_Pattern.FOLLOWER
        elif p == "LEADER":
            return Interaction_Pattern.LEADER
        elif p == "RECIPIENT":
            return Interaction_Pattern.RECIPIENT
        else:
            return Interaction_Pattern.RESCUER

    def to_int(self):
        if self == Interaction_Pattern.ASSISTANT:
            return 3
        elif self == Interaction_Pattern.COMPETITOR:
            return 12
        elif self == Interaction_Pattern.FOLLOWER:
            return 0
        elif self == Interaction_Pattern.LEADER:
            return 1
        elif self == Interaction_Pattern.RECIPIENT:
            return 2
        elif self == Interaction_Pattern.RESCUER:
            return 10


class Fatigue_Profile(Enum):
    YOUNG_HEALTHY = "y/h"
    YOUNG_SICK = "y/s"
    ELDERLY_HEALTHY = "e/h"
    ELDERLY_SICK = "e/s"
    COVID_PATIENT = "c"

    def to_int(self):
        if self == Fatigue_Profile.YOUNG_HEALTHY:
            return 1
        elif self == Fatigue_Profile.YOUNG_SICK:
            return 2
        elif self == Fatigue_Profile.ELDERLY_HEALTHY:
            return 3
        elif self == Fatigue_Profile.ELDERLY_SICK:
            return 4
        else:
            return 5

    @staticmethod
    def parse_ftg_profile(s: str):
        if s == "y/h":
            return Fatigue_Profile.YOUNG_HEALTHY
        elif s == "y/s":
            return Fatigue_Profile.YOUNG_SICK
        elif s == "e/h":
            return Fatigue_Profile.ELDERLY_HEALTHY
        elif s == "e/s":
            return Fatigue_Profile.ELDERLY_SICK
        else:
            return Fatigue_Profile.COVID_PATIENT


class FreeWill_Profile(Enum):
    NORMAL = "n"
    HIGH = "h"
    LOW = "l"
    DISABLED = "d"

    def to_int(self):
        if self == FreeWill_Profile.NORMAL:
            return 1
        elif self == FreeWill_Profile.HIGH:
            return 2
        elif self == FreeWill_Profile.LOW:
            return 3
        else:
            return -1

    @staticmethod
    def parse_fw_profile(s: str):
        if s == "n":
            return FreeWill_Profile.NORMAL
        elif s == "h":
            return FreeWill_Profile.HIGH
        elif s == "l":
            return FreeWill_Profile.LOW
        else:
            return FreeWill_Profile.DISABLED


class Human:
    def __init__(self, name: str, h_id: int, v: int, ptrn: Interaction_Pattern, p_f: Fatigue_Profile,
                 p_fw: FreeWill_Profile, start: Point, dest: Point, dext: int, same_as: int, path: int):
        self.name = name
        self.h_id = h_id
        self.v = v
        self.ptrn = ptrn
        self.p_f = p_f
        self.p_fw = p_fw
        self.start = start
        self.dest = dest
        self.dext = dext
        self.same_as = same_as
        self.path = path

    def get_constructor(self):
        if self.ptrn == Interaction_Pattern.ASSISTANT:
            return "{} = Human_Assistant({}, {}, {}, {}, {}, {});\n".format(self.name, self.h_id, self.v,
                                                                            self.p_f.to_int(),
                                                                            self.p_fw.to_int(), self.dext, self.path)
        elif self.ptrn == Interaction_Pattern.COMPETITOR:
            return "{} = Human_Competitor({}, {}, {}, {}, {});\n".format(self.name, self.h_id, self.v,
                                                                         self.p_f.to_int(),
                                                                         self.p_fw.to_int(), self.path)
        elif self.ptrn == Interaction_Pattern.FOLLOWER:
            return "{} = Human_Follower({}, {}, {}, {}, {}, {});\n".format(self.name, self.h_id, self.v,
                                                                           self.p_f.to_int(),
                                                                           self.p_fw.to_int(), self.same_as, self.path)
        elif self.ptrn == Interaction_Pattern.LEADER:
            return "{} = Human_Leader({}, {}, {}, {}, {}, {});\n".format(self.name, self.h_id, self.v,
                                                                         self.p_f.to_int(), self.p_fw.to_int(),
                                                                         self.same_as, self.path)
        elif self.ptrn == Interaction_Pattern.RECIPIENT:
            return "{} = Human_Recipient({}, {}, {}, {}, {});\n".format(self.name, self.h_id, self.v, self.p_f.to_int(),
                                                                        self.p_fw.to_int(), self.path)
        else:
            return "{} = Human_Rescuer({}, {}, {}, {}, {}, {});\n".format(self.name, self.h_id, self.v,
                                                                          self.p_f.to_int(), self.p_fw.to_int(),
                                                                          self.dext, self.path)
