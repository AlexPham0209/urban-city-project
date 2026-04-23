import pygame
from enum import Enum
from pygame import Surface
from pygame.time import Clock
from pygame.event import Event
from pygame.font import Font
import pygame_widgets
from pygame_widgets.toggle import Toggle

from city import City, Intersection, IntersectionState, Road
from dropdown_menu import DropdownMenu
from edge_menu import EdgeMenu
from emergency_toggle import EmergencyToggle
from game_state import State
from node_menu import NodeMenu
from time_input import TimeInput
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
        self.font: Font = pygame.font.SysFont("Segoe UI", 24)

        # Controls the program's state
        self.state: State = State.CREATE

        # Selections for changing the city layout
        self.first_intersection: Intersection | None = None
        self.second_intersection: Intersection | None = None
        self.selected_road: Road | None = None

        # Selections for the route
        self.start: Intersection | None = None
        self.end: Intersection | None = None

        # Mouse input
        self.mx = -1
        self.my = -1

        # Persistent states
        self.total_time: float | None = None
        self.route: list[str] | None = None
        self.current_time: tuple[int, int] = (0, 0)
        self.is_emergency: bool = False
        self.toll_cost: float = 0

        # City
        self.city = City(font=self.font)

        # Dropdown
        self.DROPDOWN_WIDTH: int = 160
        self.DROPDOWN_HEIGHT: int = 44

        self.dropdown_x: int = WIDTH - self.DROPDOWN_WIDTH // 2 - 20
        self.dropdown_y: int = 75

        self.dropdown: DropdownMenu = DropdownMenu(
            x=self.dropdown_x,
            y=self.dropdown_y,
            width=self.DROPDOWN_WIDTH,
            height=self.DROPDOWN_HEIGHT,
            screen=self.screen,
            font=self.font,
        )

        # Leftside settings
        self.left_x = 125
        self.left_y = 50

        self.time = TimeInput(
            x=self.left_x - 50, y=self.left_y, screen=self.screen, font=self.font
        )

        self.emergency_toggle = EmergencyToggle(
            x=self.left_x, y=self.left_y + 150, screen=self.screen, font=self.font
        )
        self.toll_cost_input = TollCostInput(
            x=self.left_x, y=self.left_y + 250, screen=self.screen, font=self.font
        )

        # City settings
        self.edge_menu: EdgeMenu = EdgeMenu(
            screen=self.screen, callback=self.create_edge, font=self.font
        )
        self.node_menu: NodeMenu = NodeMenu(self.screen, callback=self.create_node)

    def create_edge(self, data: dict):
        self.city.add_road(
            self.first_intersection.id,
            self.second_intersection.id,
            distance=data["distance"],
            toll_cost=data["toll_cost"],
            congestion_level=data["congestion"],
            condition=data["condition"],
            directed=data["is_one_way"],
        )
        self.edge_menu.hide()
        self.reset_selection()
        self.calculate_route()

    def create_node(self, name: str):
        if self.mx == -1 or self.my == -1:
            return

        self.city.add_intersection(name, self.mx, self.my, 25, (127, 127, 127))
        self.node_menu.hide()
        self.calculate_route()

    def edit_edge(self, data: dict):
        if not self.selected_road:
            return

        self.city.remove_road(self.selected_road.id)
        self.city.add_road(
            self.selected_road.src,
            self.selected_road.dest,
            distance=data["distance"],
            toll_cost=data["toll_cost"],
            congestion_level=data["congestion"],
            condition=data["condition"],
            directed=data["is_one_way"],
        )
        self.selected_road.selected = False
        self.selected_road = None
        self.edge_menu.hide()
        self.calculate_route()

    def edit_node(self, name: str):
        if not self.first_intersection:
            return

        self.first_intersection.state = IntersectionState.UNSELECTED
        self.first_intersection.name = name
        self.first_intersection = None
        self.calculate_route()

    def select_intersection(self, selected: Intersection):
        if len(self.city.idx_to_intersection) <= 1:
            return False

        if self.first_intersection and self.second_intersection:
            return False

        if not self.first_intersection:
            self.first_intersection = selected
            self.first_intersection.state = IntersectionState.FIRST
            return False
        else:
            self.second_intersection = selected
            self.second_intersection.state = IntersectionState.SECOND
            return True
        
    def reset_selection(self):
        self.reset_intersection(self.first_intersection)
        self.reset_intersection(self.second_intersection)

        self.first_intersection = None
        self.second_intersection = None

    def reset_intersection(self, intersection: Intersection):
        if not intersection:
            return
        
        if intersection == self.start:
            intersection.state = IntersectionState.START

        elif intersection == self.end:
            intersection.state = IntersectionState.END

        else:
            intersection.state = IntersectionState.UNSELECTED
    
        
    def select_route(self, selected: Intersection):
        if len(self.city.idx_to_intersection) <= 1:
            return False
        
        if self.start and self.end:
            return False

        if not self.start:
            self.start = selected
            self.start.state = IntersectionState.START
            return False
        else:
            self.end = selected
            self.end.state = IntersectionState.END
            return True
        
    def reset_route(self):
        if self.start:
            self.start.state = IntersectionState.UNSELECTED
        if self.end:
            self.end.state = IntersectionState.UNSELECTED

        self.start = None
        self.end = None

    def handle_create(self, event: Event):
        if event.button == 3:
            self.mx, self.my = pygame.mouse.get_pos()
            self.node_menu.show()
            return

        selected = self.city.clicked_intersection(event)

        if not selected:
            return

        if self.select_intersection(selected):
            if self.first_intersection != self.second_intersection:
                self.edge_menu.show()
            else:
                self.reset_selection()

    def handle_delete(self, event: Event):
        self.handle_intesection_delete(event)
        self.handle_road_delete(event)

    def handle_intesection_delete(self, event: Event):
        selected = self.city.clicked_intersection(event)

        if selected == self.start or selected == self.end:
            return
        
        if selected:
            self.city.remove_intersection(selected.id)
            self.calculate_route()

    def handle_road_delete(self, event: Event):
        selected = self.city.clicked_road(event)

        if selected:
            self.city.remove_road(selected.id)
            self.calculate_route()

    def handle_calculate(self, event: Event):
        selected = self.city.clicked_intersection(event)
        if not selected:
            return

        if self.start and self.end:
            self.reset_route()

        if self.select_route(selected):
            self.calculate_route()

    def calculate_route(self):
        if not self.start or not self.end:
            return
        
        self.total_time, self.total_toll_cost, self.route = (
            self.city.find_shortest_path(
                self.start.id,
                self.end.id,
                self.current_time,
                maximum_toll_cost=self.toll_cost
                if self.toll_cost_input.is_toggled
                else None,
                is_emergency=self.is_emergency,
            )
        )

    def handle_edit(self, event: Event):
        if self.edge_menu.active or self.node_menu.active:
            return

        self.handle_intersection_edit(event)
        self.handle_road_edit(event)
        

    def handle_intersection_edit(self, event: Event):
        if self.first_intersection:
            return
        
        selected = self.city.clicked_intersection(event)

        if not selected:
            return
        
        if selected == self.start or selected == self.end:
            return

        self.first_intersection = selected
        if self.first_intersection:
            self.first_intersection.state = IntersectionState.SECOND
            self.node_menu.set_options(self.first_intersection.name)
            self.node_menu.show()
        
    def handle_road_edit(self, event: Event):
        if self.selected_road:
            return

        self.selected_road = self.city.clicked_road(event)
        if self.selected_road:
            self.selected_road.selected = True
            self.edge_menu.set_options(
                self.selected_road.distance, self.selected_road.toll_cost
            )
            self.edge_menu.show()

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
        if self.total_time is None:
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
        toll_cost = (
            f"Total Toll Cost: ${self.total_toll_cost:.2f}"
            if self.total_toll_cost != -1
            else ""
        )

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
        self.time.draw()

        pygame_widgets.update(events)
        pygame.display.update()

    def update(self):
        self.toll_cost_input.on_toggled()
        self.update_time()
        self.update_emergency()
        self.update_toll_cost()
        self.calculate_route()

    def update_time(self):
        time = self.time.get_time()

        if time == self.current_time:
            return

        self.current_time = time

    def update_emergency(self):
        toggled = self.emergency_toggle.emergency_toggle.getValue()

        if toggled == self.is_emergency:
            return
        
        self.is_emergency = toggled

    def update_toll_cost(self):
        if not self.toll_cost_input.is_toggled:
            return 
        
        try: 
            value = float(self.toll_cost_input.textbox.getText() or 0)

            if not value or value == self.toll_cost:
                return
            
            self.toll_cost = value
        
        except ValueError:
            self.toll_cost = 0

    def state_changed(self):
        self.state_exit()
        self.state = self.dropdown.get_selected()
        self.state_enter()

    def state_exit(self):
        match self.state:
            case State.CREATE:
                self.reset_selection()
                self.node_menu.hide()
                self.edge_menu.hide()

            case State.DELETE:
                self.reset_selection()

            case State.CALCULATE:
                if not self.start or not self.end:
                    self.reset_route()
            
            case State.EDIT:
                self.reset_selection()

                self.node_menu.hide()
                self.edge_menu.hide()

                if self.selected_road:
                    self.selected_road.selected = False

                self.selected_road = None

            case _:
                pass

    def state_enter(self):
        match self.state:
            case State.CREATE:
                self.node_menu.callback = self.create_node
                self.edge_menu.callback = self.create_edge
                self.node_menu.button.setText("Create Intersection")
                self.edge_menu.button.setText("Create Road")

            case State.DELETE:
                pass

            case State.CALCULATE:
                pass

            case State.EDIT:
                self.node_menu.callback = self.edit_node
                self.edge_menu.callback = self.edit_edge
                self.node_menu.button.setText("Edit Intersection")
                self.edge_menu.button.setText("Edit Road")

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
