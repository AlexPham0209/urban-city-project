import pygame
from pygame import Surface
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button


class NodeMenu:
    BG_COLOR = (245, 245, 245)
    BORDER_COLOR = (200, 200, 200)
    PADDING = 40

    def __init__(self, screen: Surface, callback):
        self.screen = screen
        self.callback = callback
        self.active = False
        
        # Layout positioning (top-center)
        self.y = 20

        input_width = 240
        button_width = 180
        height = 44

        # Text input
        self.name_textbox = TextBox(
            screen,
            (screen.get_width() - input_width) // 2,
            self.y + self.PADDING - height // 2,
            input_width,
            height,
            fontSize=24,
            borderColour=(180, 180, 180),
            textColour=(30, 30, 30),
            radius=8,
            borderThickness=2,
            placeholderText="Name",
        )

        # Button
        self.button = Button(
            screen,
            (screen.get_width() - button_width) // 2,
            self.name_textbox.getY() + height + self.PADDING - height // 2,
            button_width,
            height,
            text="Add Intersection",
            fontSize=22,
            radius=8,
            borderThickness=0,
            inactiveColour=(70, 130, 180),   # steel blue
            hoverColour=(90, 150, 210),
            pressedColour=(50, 110, 160),
            textColour=(255, 255, 255),
            onClick=self.on_click,
        )

    
        self.hide()

    # --------------------------
    # Logic
    # --------------------------
    def on_click(self):
        if not self.active:
            return

        text = self.name_textbox.getText().strip()

        if len(text):
            self.callback(text)
            self.hide()
        
        else:
            # Simple visual feedback
            self.name_textbox.setText("")
            self.name_textbox.placeholderText = "Enter valid name"

    # --------------------------
    # Visibility
    # --------------------------
    def show(self):
        self.active = True
        self.name_textbox.enable()
        self.button.enable()
        self.name_textbox.show()
        self.button.show()

    def hide(self):
        self.active = False
        self.name_textbox.setText("")
        self.name_textbox.disable()
        self.button.disable()
        self.name_textbox.hide()
        self.button.hide()

    # --------------------------
    # Rendering (Custom UI Panel)
    # --------------------------
    def draw(self):
        if not self.active:
            return

        # Panel background (card style)
        pygame.draw.rect(
            self.screen,
            self.BG_COLOR,
            (self.x, self.y, self.WIDTH, self.HEIGHT),
            border_radius=12,
        )

        pygame.draw.rect(
            self.screen,
            self.BORDER_COLOR,
            (self.x, self.y, self.WIDTH, self.HEIGHT),
            width=2,
            border_radius=12,
        )

        # Title
        font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        text_surface = font.render("Add Intersection", True, (40, 40, 40))
        self.screen.blit(
            text_surface,
            (self.x + self.PADDING, self.y + 8),
        )