from pygame import Surface
from pygame.font import Font
from pygame_widgets.textbox import TextBox

from city import CongestionLevel


class TollCostInput:
    def __init__(self, screen: Surface, font: Font):
        self.width: int = 200
        self.height: int = 44

        self.x = 0
        self.y = 100

        self.screen = screen
        self.font = font

        self.textbox: TextBox = TextBox(
            self.screen,
            self.x,
            self.y,
            self.width,
            self.height,
            fontSize=24,
            borderColour=(180, 180, 180),
            textColour=(30, 30, 30),
            radius=8,
            borderThickness=2,
            placeholderText="Maximum Toll Cost",
        )


