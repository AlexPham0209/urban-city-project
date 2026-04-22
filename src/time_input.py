from pygame_widgets.textbox import TextBox
from pygame.font import Font
from pygame import Surface


class TimeInput:
    def __init__(self, x: int, y: int, screen: Surface, font: Font):
        self.screen = screen
        self.font = font

        # Labels
        self.hour_label = self.font.render("Hour (0-23):", True, (0, 0, 0))
        self.min_label = self.font.render("Min (0-59):", True, (0, 0, 0))

        self.width = 50
        self.height = 35

        self.left_x = 125
        self.left_y = 75

        # Hour TextBox
        self.hour_box = TextBox(
            screen,
            (x + 130),
            y - self.height // 2,
            self.width,
            self.height,
            fontSize=20,
            borderColour=(170, 170, 170),
            textColour=(0, 0, 0),
            onSubmit=lambda: print(f"Hour set to: {self.hour_box.getText()}"),
            radius=5,
        )

        # Minute TextBox
        self.min_box = TextBox(
            screen,
            (x + 130),
            (y + 50) - self.height // 2,
            self.width,
            self.height,
            fontSize=20,
            borderColour=(170, 170, 170),
            textColour=(0, 0, 0),
            onSubmit=lambda: print(f"Minute set to: {self.min_box.getText()}"),
            radius=5,
        )

        self.x = x
        self.y = y

    def get_time(self) -> tuple[int, int]:
        """Returns (hour, minute) as integers, defaulting to 0 if invalid."""
        try:
            h = int(self.hour_box.getText())
            m = int(self.min_box.getText())
            return max(0, min(23, h)), max(0, min(59, m))
        except ValueError:
            return 0, 0

    def draw(self):
        self.screen.blit(
            self.hour_label,
            (
                self.x,
                self.y - self.hour_label.get_height() // 2,
            ),
        )
        self.screen.blit(
            self.min_label,
            (
                self.x,
                (self.y + 50) - self.min_label.get_height() // 2,
            ),
        )
