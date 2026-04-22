from collections import defaultdict
from dataclasses import astuple, dataclass
from enum import Enum
import heapq
import math
from typing import Optional, Self

import pygame
from pygame import Surface, gfxdraw
from pygame.event import Event
from pygame.font import Font


class CongestionLevel(Enum):
    BUSY = 10.0
    NON_BUSY = 20.0


class IntersectionState(Enum):
    UNSELECTED = 1
    FIRST = 2
    SECOND = 3


class RoadCondition(Enum):
    CLEAR = 0
    CLOSURE = 1
    ACCIDENT = 2
    CONSTRUCTION = 3


@dataclass
class Road:
    id: int
    src: int
    dest: int
    distance: float
    congestion_level: CongestionLevel
    condition: RoadCondition
    toll_cost: Optional[float]
    closed: bool
    reversed: bool
    is_one_way: bool
    selected: bool = False

    def get_cost(self) -> float:
        return self.distance / self.congestion_level.value

    def __lt__(self, other: Self) -> bool:
        return self.distance <= other.distance

    def __hash__(self):
        return self.id


@dataclass
class Intersection:
    id: int
    name: str
    x: int
    y: int
    radius: int
    color: tuple[int, int, int]
    state: IntersectionState = IntersectionState.UNSELECTED

    def draw(self, screen: Surface, font: Font):
        gfxdraw.filled_circle(
            screen,
            self.x,
            self.y,
            self.radius,
            (0, 0, 0),
        )

        gfxdraw.aacircle(
            screen,
            self.x,
            self.y,
            self.radius,
            (0, 0, 0),
        )

        color = None
        match self.state:
            case IntersectionState.UNSELECTED:
                color = self.color
            case IntersectionState.FIRST:
                color = (255, 0, 0)
            case IntersectionState.SECOND:
                color = (0, 255, 0)

        # Inner circle
        gfxdraw.filled_circle(
            screen,
            self.x,
            self.y,
            self.radius - 2,
            color,
        )

        gfxdraw.aacircle(
            screen,
            self.x,
            self.y,
            self.radius - 2,
            color,
        )

        text_surface = font.render(f"{self.name}", True, (0, 0, 0))
        width, height = font.size(f"{self.name}")
        screen.blit(text_surface, (self.x - width // 2, self.y - height // 2 - 50))

    def mouse_enter(self):
        mx, my = pygame.mouse.get_pos()
        distance = math.sqrt((self.x - mx) ** 2 + (self.y - my) ** 2)
        return distance <= self.radius

    def clicked(self, event: Event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.mouse_enter()
        )

    def __eq__(self, other: Self):
        return self.name == other.name

    def __hash__(self):
        return self.id

    def __repr__(self):
        return self.name


class City:
    def __init__(self, font: Font):
        self.nodes = 0
        self.intersections_to_idx: dict[Intersection, int] = {}
        self.idx_to_intersection: dict[int, Intersection] = {}

        self.edges = 0
        self.road_to_idx: dict[Road, int] = {}
        self.idx_to_road: dict[int, Road] = {}

        self.adj: dict[int, set[Road]] = defaultdict(set)
        self.font: Font = font

    # --------------------------
    # Rendering
    # --------------------------
    def draw(self, screen: Surface):
        for start, roads in self.adj.items():
            a = self.idx_to_intersection[start]

            for road in roads:
                b = self.idx_to_intersection[road.dest]

                if road.reversed:
                    continue

                color = None
                match road.congestion_level:
                    case CongestionLevel.NON_BUSY:
                        color = (0, 255, 0)
                    case CongestionLevel.BUSY:
                        color = (255, 0, 0)
                    case _:
                        color = (255, 0, 0)

                if road.selected:
                    color = (0, 0, 255)

                # Draw road
                pygame.draw.line(screen, color, (a.x, a.y), (b.x, b.y), width=2)

                # Draw distance label
                self._draw_road_label(screen, a, b, road)

        for intersection in self.idx_to_intersection.values():
            intersection.draw(screen, self.font)

    def _draw_road_label(
        self, screen: Surface, a: Intersection, b: Intersection, road: Road
    ):
        miles = f"{road.distance} mi."
        toll_cost = f"${road.toll_cost:.2f}"
        miles_surface = self.font.render(miles, True, (0, 0, 0))
        toll_cost_surface = self.font.render(toll_cost, True, (0, 0, 0))
        miles_width, miles_height = self.font.size(miles)
        toll_width, toll_height = self.font.size(toll_cost)

        dx, dy = b.x - a.x, b.y - a.y
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        nx, ny = dx / dist, dy / dist

        screen.blit(
            miles_surface,
            (
                a.x + dx // 2 - miles_width // 2 + int(ny * 75),
                a.y + dy // 2 - miles_height // 2 - int(nx * 75),
            ),
        )

        screen.blit(
            toll_cost_surface,
            (
                a.x + dx // 2 - miles_width // 2 + int(ny * 75),
                a.y + dy // 2 - miles_height // 2 - int(nx * 75) + 25,
            ),
        )

    # --------------------------
    # Interaction
    # --------------------------
    def clicked_intersection(self, event: Event) -> Optional[Intersection]:
        return next(
            (i for i in self.idx_to_intersection.values() if i.clicked(event)),
            None,
        )

    def clicked_road(self, event: Event) -> Optional[Intersection]:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        mx, my = pygame.mouse.get_pos()

        for start, roads in self.adj.items():
            a = self.idx_to_intersection[start]

            for road in roads:
                if road.reversed:
                    continue

                b = self.idx_to_intersection[road.dest]
                dx, dy = b.x - a.x, b.y - a.y

                distance = abs(dy * mx - dx * my + b.x * a.y - b.y * a.x) / math.sqrt(
                    dy**2 + dx**2
                )

                if distance < 10:
                    return road

    # --------------------------
    # Graph Mutations
    # --------------------------
    def add_intersection(self, name: str, x: int, y: int, radius: int, color):
        intersection = Intersection(self.nodes, name, x, y, radius, color)
        self.idx_to_intersection[self.nodes] = intersection
        self.intersections_to_idx[intersection] = self.nodes
        self.nodes += 1
        return True

    def remove_intersection(self, id: int):
        self.idx_to_intersection.pop(id, None)
        self.adj.pop(id, None)

        for node in self.adj:
            self.adj[node] = [r for r in self.adj[node] if r.dest != id]

    def add_road(
        self,
        a: int,
        b: int,
        distance: float,
        congestion_level: CongestionLevel = CongestionLevel.NON_BUSY,
        condition: RoadCondition = RoadCondition.CLEAR,
        toll_cost: float = 0.0,
        directed: bool = True,
        closed: bool = False,
    ):
        if a not in self.idx_to_intersection or b not in self.idx_to_intersection:
            return

        road = Road(
            self.edges,
            a,
            b,
            distance,
            congestion_level,
            condition,
            toll_cost,
            closed,
            False,
            directed,
        )
        self.idx_to_road[self.edges] = road
        self.road_to_idx[road] = self.edges
        self.adj[a].add(road)
        self.edges += 1

        reverse = Road(
            self.edges,
            b,
            a,
            distance,
            congestion_level,
            condition,
            toll_cost,
            closed,
            True,
            directed,
        )
        self.idx_to_road[self.edges] = reverse
        self.road_to_idx[reverse] = self.edges
        self.adj[b].add(reverse)
        self.edges += 1

    def remove_road(self, id: int):
        if id not in self.idx_to_road:
            return

        road = self.idx_to_road[id]
        self.idx_to_road.pop(id, None)
        self.adj.pop(id, None)

        for _, roads in self.adj.items():
            if road in roads:
                roads.remove(road)

        if id + 1 not in self.idx_to_road:
            return

        reversed = self.idx_to_road[id + 1]

        if not reversed.reversed:
            return

        self.idx_to_road.pop(id + 1, None)
        self.adj.pop(id + 1, None)

        for _, roads in self.adj.items():
            if reversed in roads:
                roads.remove(reversed)

    def find_shortest_path(
        self,
        src: int,
        dest: int,
        maximum_toll_cost: float | None = None,
        is_emergency: bool = False,
    ) -> tuple[float, float, list[float]]:
        q = []
        dist = {}
        dist[src] = 0

        if src not in self.idx_to_intersection or dest not in self.idx_to_intersection:
            return -1, -1, []

        # State: (Time, Toll Cost, Intersection, Path)
        q.append((0, 0, src, [self.idx_to_intersection[src].name]))

        while q:
            time, total_toll_cost, curr, path = heapq.heappop(q)

            if curr == dest:
                return time, total_toll_cost, path

            for road in self.adj[curr]:
                (
                    id,
                    src,
                    dst,
                    _,
                    _,
                    condition,
                    toll_cost,
                    closed,
                    reversed,
                    is_one_way,
                    _,
                ) = astuple(road)

                # Can't exceed past certain toll cost
                if (
                    maximum_toll_cost != None
                    and total_toll_cost + toll_cost > maximum_toll_cost
                ):
                    continue

                # Can't go past if road is closed
                if closed:
                    continue

                # Can't go past if road is one way and not an emergency vehicle
                if reversed and is_one_way and not is_emergency:
                    continue

                if dst not in dist or time + road.get_cost() < dist[dst]:
                    dist[dst] = time + road.get_cost()
                    next_toll_cost = total_toll_cost
                    if not is_emergency:
                        next_toll_cost += toll_cost

                    heapq.heappush(
                        q,
                        (
                            dist[dst],
                            next_toll_cost,
                            dst,
                            path + [self.idx_to_intersection[dst].name],
                        ),
                    )

        return -1, -1, []

    # def find_shortest_paths() -> list[list[float]]:
