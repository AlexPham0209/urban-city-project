from pygame import Surface
from pygame.font import Font
from pygame_widgets.toggle import Toggle

from city import CongestionLevel


class EmergencyToggle:
    def __init__(self, x: int, y: int, screen: Surface, font: Font):
        self.width: int = 60
        self.height: int = 30

        self.x = x
        self.y = y

        self.screen = screen
        self.font = font

        self.emergency_toggle: Toggle = Toggle(
            self.screen,
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height,
            fontSize=24,
            borderColour=(180, 180, 180),
            textColour=(30, 30, 30),
            radius=8,
            borderThickness=2,
            text="Is Emergency Vehicle",
        )

    def draw(self):
        self.emergency_toggle.draw()

        text_surface = self.font.render("Is Emergency Vehicle", True, (40, 40, 40))
        self.screen.blit(
            text_surface,
            (
                self.x - text_surface.get_width() // 2,
                self.y - text_surface.get_height() // 2 - 40,
            ),
        )
