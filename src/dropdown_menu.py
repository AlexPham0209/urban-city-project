import pygame

from game_state import State
from pygame_widgets.dropdown import Dropdown
from pygame.font import Font
from pygame import Surface


class DropdownMenu:
    def __init__(
        self, x: int, y: int, width: int, height: int, screen: Surface, font: Font
    ):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.screen = screen
        self.font = font

        self.dropdown = Dropdown(
            self.screen,
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height,
            name="Mode",
            choices=["Create", "Delete", "Calculate", "Edit"],
            values=[State.CREATE, State.DELETE, State.CALCULATE, State.EDIT],
            # Typography
            font=self.font,
            textHAlign="centre",
            # Colors (modern palette)
            colour=(225, 225, 225),
            borderColour=(200, 200, 200),
            textColour=(40, 40, 40),
            # Dropdown options
            colourSelected=(220, 235, 250),
            colourHover=(230, 240, 255),
            # Shape
            borderRadius=10,
            # Behavior
            direction="down",
        )

    def draw(self):
        panel_width = 180
        panel_height = 90
        panel_x = self.x - self.width // 2 - 10
        panel_y = self.y - self.height // 2 - 40

        # Background card
        pygame.draw.rect(
            self.screen,
            (250, 250, 250),
            (panel_x, panel_y, panel_width, panel_height),
            border_radius=12,
        )

        # Border
        pygame.draw.rect(
            self.screen,
            (210, 210, 210),
            (panel_x, panel_y, panel_width, panel_height),
            width=2,
            border_radius=12,
        )

        # Label
        label = self.font.render("Mode", True, (80, 80, 80))
        self.screen.blit(label, (panel_x + 10, panel_y + 8))

    def get_selected(self) -> State:
        return self.dropdown.getSelected()
