from typing import List


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Area:
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        self.corners = [p1, p2, p3, p4]


class Layout:
    def __init__(self, areas: List[Area], inter_pts: List[Point]):
        self.areas = areas
        self.inter_pts = inter_pts
