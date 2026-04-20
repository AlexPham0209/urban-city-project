import pygame
from enum import Enum
from pygame import Surface
from pygame.time import Clock
from pygame.event import Event
from pygame.font import Font
import pygame_widgets
from pygame_widgets.toggle import Toggle

from city import City, Intersection, IntersectionState
from dropdown_menu import DropdownMenu
from edge_menu import EdgeMenu
from emergency_toggle import EmergencyToggle
from game_state import State
from node_menu import NodeMenu
from toll_cost import TollCostInput

# Constants
WIDTH, HEIGHT = 960, 720
FPS = 60


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen: Surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Urban Traffic Visualization")
        self.clock: Clock = Clock()

        self.start: Intersection | None = None
        self.end: Intersection | None = None
        self.total_time: float | None = None
        self.route: list[str] | None = None

        self.font: Font = pygame.font.SysFont("Segoe UI", 24)

        self.state: State = State.CREATE

        self.DROPDOWN_WIDTH: int = 160
        self.DROPDOWN_HEIGHT: int = 44

        self.mx = -1
        self.my = -1

        self.dropdown_x: int = WIDTH - self.DROPDOWN_WIDTH - 20
        self.dropdown_y: int = 50

        self.dropdown: DropdownMenu = DropdownMenu(
            x=self.dropdown_x,
            y=self.dropdown_y,
            width=self.DROPDOWN_WIDTH,
            height=self.DROPDOWN_HEIGHT,
            screen=self.screen,
            font=self.font,
        )

        self.emergency_toggle = EmergencyToggle(screen=self.screen, font=self.font)
        self.toll_cost_input = TollCostInput(screen=self.screen, font=self.font)

        self.city = City(font=self.font)
        self.edge_menu: EdgeMenu = EdgeMenu(self.screen, self.create_edge, self.font)
        self.node_menu: NodeMenu = NodeMenu(self.screen, self.create_node)

    def create_edge(self, data: dict):
        self.city.add_road(self.start.name, self.end.name, distance=data["distance"], toll_cost=data["toll_cost"], congestion_level=data["congestion"], directed=data["is_one_way"])
        self.edge_menu.hide()
        self.reset_selection()

    def create_node(self, name: str):
        if self.mx == -1 or self.my == -1:
            return

        self.city.add_intersection(name, self.mx, self.my, 25, (127, 127, 127))

    def edit_edge(self, data: dict):
        print(data)

    def edit_node(self, name: str):
        if not self.start:
            return
        
        self.start.state = IntersectionState.UNSELECTED
        self.start.name = name
        self.start = None
    
    def reset_selection(self):
        if self.start:
            self.start.state = IntersectionState.UNSELECTED
        if self.end:
            self.end.state = IntersectionState.UNSELECTED

        self.start = None
        self.end = None

    def select_intersection(self, selected: Intersection):
        if len(self.city.intersections) <= 1:
            return False
    
        if not self.start:
            self.start = selected
            self.start.state = IntersectionState.FIRST
            return False
        else:
            self.end = selected
            self.end.state = IntersectionState.SECOND
            return True

    def handle_create(self, event: Event):
        if event.button == 3:
            self.mx, self.my = pygame.mouse.get_pos()
            self.node_menu.show()
            return

        selected = self.city.clicked_intersection(event)
        self.city.clicked_road(event)
        if not selected:
            return
        
        if self.select_intersection(selected):
            if self.start != self.end:
                self.edge_menu.show()
            else:
                self.reset_selection()

    def handle_delete(self, event: Event):
        selected = self.city.clicked_intersection(event)
        if selected:
            self.city.remove_intersection(selected.name)

    def handle_calculate(self, event: Event):
        selected = self.city.clicked_intersection(event)
        if not selected:
            return

        if self.select_intersection(selected):
            self.total_time, self.total_toll_cost, self.route = self.city.find_shortest_path(
                self.start.name,
                self.end.name,
                maximum_toll_cost=float(self.toll_cost_input.textbox.getText()) or None if self.toll_cost_input.is_toggled else None,
                is_emergency=self.emergency_toggle.emergency_toggle.getValue(),
            )
            self.reset_selection()

    def handle_edit(self, event: Event):
        if self.start:
            return

        self.start = self.city.clicked_intersection(event)
        
        if self.start:
            self.start.state = IntersectionState.SECOND
            self.node_menu.show()

    def handle_mouse_event(self, event: Event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        match self.state:
            case State.CREATE:
                self.handle_create(event)
            case State.DELETE:
                self.handle_delete(event)
            case State.CALCULATE:
                self.handle_calculate(event)
            case State.EDIT:
                self.handle_edit(event)

    def draw_distance(self):
        if self.total_time is None or self.state != State.CALCULATE:
            return

        y = 10
        padding = 60

        total_minutes = round(self.total_time * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        time = (
            f"{f'{hours} hours, ' if hours != 0 else ''} {minutes} minutes"
            if self.total_time != -1 and self.route
            else "No route to destination"
        )
        route = f"Route: {', '.join(self.route)}" if self.route else ""
        toll_cost = f"Total Toll Cost: ${self.total_toll_cost:.2f}" if self.total_toll_cost != -1 else ""

        time_surface = self.font.render(time, True, (0, 0, 0))
        route_surface = self.font.render(route, True, (0, 0, 0))
        toll_cost_surface = self.font.render(toll_cost, True, (0, 0, 0))

        time_width, time_height = self.font.size(time)
        route_width, route_height = self.font.size(route)
        toll_cost_width, toll_cost_height = self.font.size(toll_cost)


        self.screen.blit(
            time_surface, (WIDTH // 2 - time_width // 2, y + time_height // 2)
        )
        self.screen.blit(
            route_surface,
            (
                WIDTH // 2 - route_width // 2,
                y + time_height + padding - route_height // 2,
            ),
        )

        self.screen.blit(
            toll_cost_surface,
            (
                WIDTH // 2 - toll_cost_width // 2, 
                y + time_height + route_height + padding - toll_cost_height // 2,
            ),
        )   

    def draw_grid(self, spacing=40, color=(220, 220, 220)):
        for x in range(0, WIDTH, spacing):
            pygame.draw.line(self.screen, color, (x, 0), (x, HEIGHT))

        for y in range(0, HEIGHT, spacing):
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

    def render(self, events):
        self.screen.fill((255, 255, 255))

        self.draw_grid()
        self.city.draw(self.screen)
        self.dropdown.draw()
        self.emergency_toggle.draw()
        self.edge_menu.draw()
        self.toll_cost_input.draw()
        self.draw_distance()
        # self.node_menu.draw()

        pygame_widgets.update(events)
        pygame.display.update()

    def update(self):
        self.toll_cost_input.on_toggled()

    def state_changed(self):
        self.state_exit()
        self.state = self.dropdown.get_selected()
        self.state_enter()

    def state_exit(self):
        match self.state:
            case State.CREATE:
                self.start = None
                self.end = None
                self.node_menu.hide()
                self.edge_menu.hide()

            case State.DELETE:
                self.start = None
                self.end = None

            case State.CALCULATE:
                self.start = None
                self.end = None
                self.total_time = None
                self.route = None

            case State.EDIT:
                if self.start:
                    self.start.state = IntersectionState.UNSELECTED

                self.start = None
                self.end = None
                self.node_menu.hide()
                self.edge_menu.hide()
                
            case _:
                pass

    def state_enter(self):
        match self.state:
            case State.CREATE:
                self.node_menu.callback = self.create_node
                self.edge_menu.callback = self.create_edge
                self.node_menu.button.setText("Create Intersection")

            case State.DELETE:
                pass

            case State.CALCULATE:
                pass

            case State.EDIT:
                self.node_menu.callback = self.edit_node
                self.edge_menu.callback = self.edit_edge
                self.node_menu.button.setText("Edit Intersection")
                
            case _:
                pass

    def run(self):
        running = True

        while running:
            events = pygame.event.get()

            if self.dropdown.get_selected() != self.state:
                self.state_changed()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                self.handle_mouse_event(event)

            self.update()
            self.render(events)
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    Game().run()
