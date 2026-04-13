import pygame
from pygame import Surface
from pygame.freetype import Font
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle
from pygame_widgets.dropdown import Dropdown

from city import CongestionLevel


class EdgeMenu:
    # Increased height to fit new rows
    WIDTH = 380
    HEIGHT = 280
    PADDING = 15

    BG_COLOR = (245, 245, 245)
    BORDER_COLOR = (200, 200, 200)

    def __init__(self, screen: Surface, callback, font: Font):
        self.screen = screen
        self.callback = callback
        self.font = font
        self.active = False

        self.x = (screen.get_width() - self.WIDTH) // 2
        self.y = 20

        input_width = 180
        button_width = 140
        height = 35  # Slightly shorter to save vertical space

        # 1. Distance Input
        self.weight_textbox = TextBox(
            screen,
            self.x + self.PADDING,
            self.y + 40,
            input_width,
            height,
            fontSize=20,
            borderColour=(180, 180, 180),
            radius=5,
            placeholderText="Distance (mi)",
        )

        # 2. Toll Cost Input
        self.toll_cost = TextBox(
            screen,
            self.x + self.PADDING,
            self.weight_textbox.getY() + height + self.PADDING,
            input_width,
            height,
            fontSize=20,
            borderColour=(180, 180, 180),
            radius=5,
            placeholderText="Toll Cost ($)",
        )

        # 3. Congestion Level (1.0 = clear, 2.0 = heavy traffic)
        self.congestion_input = Dropdown(
            screen,
            self.x + self.PADDING,
            self.toll_cost.getY() + height + self.PADDING,
            input_width,
            height,
            fontSize=20,
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
            name="Congestion Level",
            choices=["Busy", "Non-Busy"],
            values=[CongestionLevel.BUSY, CongestionLevel.NON_BUSY],
        )

        # 4. One-Way Toggle (Positioned to the right of inputs)
        self.one_way_toggle = Toggle(
            self.screen,
            self.x + self.WIDTH - 80,
            self.weight_textbox.getY() + 5,
            60,
            25,
            startOn=False,
        )

        # 5. Submit Button
        self.button = Button(
            screen,
            (screen.get_width() - button_width) // 2,
            self.y + self.HEIGHT - height - self.PADDING,
            button_width,
            height,
            text="Add Road",
            fontSize=20,
            radius=8,
            inactiveColour=(70, 130, 180),
            hoverColour=(90, 150, 210),
            pressedColour=(50, 110, 160),
            textColour=(255, 255, 255),
            onClick=self.on_click,
        )

        self.hide()

    def on_click(self):
        if not self.active:
            return

        try:
            # Gather and validate data
            dist = float(self.weight_textbox.getText())
            toll = float(self.toll_cost.getText() or 0)
            cong = self.congestion_input.getSelected()
            is_one_way = self.one_way_toggle.getValue()

            if dist <= 0:
                raise ValueError
            
            if not cong:
                cong = CongestionLevel.NON_BUSY
            
            # Package data for the callback
            data = {
                "distance": dist,
                "toll_cost": toll,
                "congestion": cong,
                "is_one_way": is_one_way,
            }

            self.callback(data)
            self.hide()

        except ValueError:
            self.weight_textbox.setText("")
            self.weight_textbox.placeholderText = "Check Inputs!"

    def show(self):
        self.active = True
        for widget in [
            self.weight_textbox,
            self.toll_cost,
            self.congestion_input,
            self.button,
            self.one_way_toggle,
        ]:
            widget.enable()
            widget.show()

    def hide(self):
        self.active = False
        for widget in [
            self.weight_textbox,
            self.toll_cost,
            self.congestion_input,
            self.one_way_toggle,
        ]:
            if hasattr(widget, "setText"):
                widget.setText("")
            widget.disable()
            widget.hide()

        self.button.disable()
        self.button.hide()

    def draw(self):
        if not self.active:
            return

        # Background Panel
        # pygame.draw.rect(self.screen, self.BG_COLOR, (self.x, self.y, self.WIDTH, self.HEIGHT), border_radius=12)
        # pygame.draw.rect(self.screen, self.BORDER_COLOR, (self.x, self.y, self.WIDTH, self.HEIGHT), width=2, border_radius=12)

        # Labels
        small_font = pygame.font.SysFont("Segoe UI", 14)

        # self.screen.blit(self.font.render("Road Settings", True, (40, 40, 40)), (self.x + self.PADDING, self.y + 10))

        # Label for Toggle
        toggle_label = small_font.render("One-Way", True, (60, 60, 60))
        self.screen.blit(
            toggle_label, (self.one_way_toggle.getX(), self.one_way_toggle.getY() - 18)
        )
