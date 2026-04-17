from pygame import Surface
from pygame.font import Font
from pygame_widgets.textbox import TextBox

from city import CongestionLevel

from pygame_widgets.toggle import Toggle


class TollCostInput:
    def __init__(self, screen: Surface, font: Font):
        self.width: int = 200
        self.height: int = 44

        self.x = 0
        self.y = 200

        self.screen = screen
        self.font = font

        self.toggle_width = 60
        self.toggle_height = 30
        self.toggle_x = self.toggle_width + 20
        self.toggle_y = self.y

        self.is_toggled = False

        self.toggle: Toggle = Toggle(
            self.screen,
            self.toggle_x,
            self.toggle_y,
            self.toggle_width,
            self.toggle_height,
            fontSize=24,
            borderColour=(180, 180, 180),
            textColour=(30, 30, 30),
            radius=8,
            borderThickness=2,
            text="Minimize Toll Cost",
            startOn=False
        )

        self.textbox: TextBox = TextBox(
            self.screen,
            self.x,
            self.toggle_y + self.toggle_height + 20,
            self.width,
            self.height,
            fontSize=24,
            borderColour=(180, 180, 180),
            textColour=(30, 30, 30),
            radius=8,
            borderThickness=2,
            placeholderText="Maximum Toll Cost",
        )


    def on_toggled(self):      
        if self.on_toggled == self.toggle.getValue():
            return
        self.is_toggled = self.toggle.getValue()
        
        if not self.is_toggled:
            self.textbox.hide()
        else:
            self.textbox.show()
    
    def draw(self):
        self.toggle.draw()

        text_surface = self.font.render("Minimize Toll Cost", True, (40, 40, 40))
        self.screen.blit(
            text_surface,
            (
                self.toggle_x + self.toggle_width // 2 - text_surface.get_width() // 2,
                self.toggle_y - self.toggle_height // 2 - text_surface.get_height() // 2 - 10,
            ),
        )


