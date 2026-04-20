import pygame
from pygame import Surface
from pygame.freetype import Font
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle
from pygame_widgets.dropdown import Dropdown

# Assuming these exist in your city.py
from city import CongestionLevel, RoadCondition 

class EdgeMenu:
    # Increased height to fit the second dropdown comfortably
    WIDTH = 400
    HEIGHT = 360
    PADDING = 20

    # Modern Color Palette
    BG_COLOR = (252, 252, 252)
    HEADER_COLOR = (70, 130, 180)
    TEXT_COLOR = (45, 45, 45)
    BORDER_COLOR = (220, 220, 220)
    SHADOW_COLOR = (0, 0, 0, 30)

    def __init__(self, screen: Surface, callback, font: Font):
        self.screen = screen
        self.callback = callback
        self.font = font
        self.active = False

        self.x = (screen.get_width() - self.WIDTH) // 2
        self.y = 20

        input_width = 200
        height = 35
        
        # UI Styling variables
        widget_style = {
            "fontSize": 18,
            "borderColour": (200, 200, 200),
            "radius": 5,
            "colour": (255, 255, 255)
        }

        # 1. Distance Input
        self.weight_textbox = TextBox(
            screen, self.x + self.PADDING, self.y, input_width, height,
            placeholderText="Distance (mi)", **widget_style
        )

        # 2. Toll Cost Input
        self.toll_cost = TextBox(
            screen, self.x + self.PADDING, self.weight_textbox.getY() + height + self.PADDING,
            input_width, height, placeholderText="Toll Cost ($)", **widget_style
        )

        # 3. Congestion Dropdown
        self.congestion_input = Dropdown(
            screen, self.x + self.PADDING, self.toll_cost.getY() + height + self.PADDING,
            input_width, height, name="Traffic Level",
            font=self.font,
            colour=(225, 225, 225),
            borderColour=(200, 200, 200),
            textColour=(40, 40, 40),
            # Dropdown options
            colourSelected=(220, 235, 250),
            colourHover=(230, 240, 255),
            choices=["Busy", "Non Busy"],
            values=[CongestionLevel.BUSY, CongestionLevel.NON_BUSY],
            borderRadius=5, fontSize=18, direction="down"
        )

        # 4. Road Condition Dropdown (NEW)
        self.road_condition = Dropdown(
            screen, self.x + self.PADDING, self.congestion_input.getY() + height + self.PADDING,
            input_width, height, name="Road Condition",
            font=self.font,
            colour=(225, 225, 225),
            borderColour=(200, 200, 200),
            textColour=(40, 40, 40),
            # Dropdown options
            colourSelected=(220, 235, 250),
            colourHover=(230, 240, 255),
            choices=["Clear", "Closure", "Accident"],
            values=[RoadCondition.CLEAR, RoadCondition.CLOSURE, RoadCondition.ACCIDENT],
            borderRadius=5, fontSize=18, direction="down"
        )

        # 5. One-Way Toggle
        self.one_way_toggle = Toggle(
            screen, self.x + self.WIDTH - 80, self.weight_textbox.getY() + 5,
            50, 22, startOn=False
        )

        # 6. Submit Button
        self.button = Button(
            screen, self.x + (self.WIDTH - 150) // 2, self.y + self.HEIGHT - 55,
            150, 40, text="Create Road", fontSize=20, radius=10,
            inactiveColour=self.HEADER_COLOR,
            hoverColour=(90, 150, 210),
            pressedColour=(50, 110, 160),
            textColour=(255, 255, 255),
            onClick=self.on_click,
        )

        self.hide()

    def on_click(self):
        if not self.active: return
        try:
            dist = float(self.weight_textbox.getText())
            toll = float(self.toll_cost.getText() or 0)
            cong = self.congestion_input.getSelected() or CongestionLevel.NON_BUSY
            cond = self.road_condition.getSelected() or RoadCondition.CLEAR
            is_one_way = self.one_way_toggle.getValue() or False

            if dist <= 0: raise ValueError
            
            data = {
                "distance": dist,
                "toll_cost": toll,
                "congestion": cong,
                "condition": cond,
                "is_one_way": is_one_way,
            }

            self.callback(data)
            self.hide()
        except ValueError:
            self.weight_textbox.setText("")
            self.weight_textbox.placeholderText = "Invalid Input!"

    def show(self):
        self.active = True
        for w in [self.weight_textbox, self.toll_cost, self.congestion_input, 
                  self.road_condition, self.button, self.one_way_toggle]:
            w.enable()
            w.show()

    def hide(self):
        self.active = False
        for w in [self.weight_textbox, self.toll_cost, self.congestion_input, 
                  self.road_condition, self.one_way_toggle, self.button]:
            # if hasattr(w, "setText"): w.setText("")
            w.disable()
            w.hide()

    def draw(self):
        if not self.active: return

        # Draw Shadow
        # shadow_rect = pygame.Rect(self.x + 4, self.y + 4, self.WIDTH, self.HEIGHT)
        # pygame.draw.rect(self.screen, (220, 220, 220), shadow_rect, border_radius=15)

        # # Draw Main Background
        # main_rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        # pygame.draw.rect(self.screen, self.BG_COLOR, main_rect, border_radius=15)
        # pygame.draw.rect(self.screen, self.BORDER_COLOR, main_rect, width=2, border_radius=15)

        # # Draw Header Bar
        # header_rect = pygame.Rect(self.x, self.y, self.WIDTH, 45)
        # pygame.draw.rect(self.screen, self.HEADER_COLOR, header_rect, 
        #                  border_top_left_radius=15, border_top_right_radius=15)

        # Labels
        title_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
        label_font = pygame.font.SysFont("Segoe UI", 14)

        # Header Title
        # title_surf = title_font.render("Road Configuration", True, (255, 255, 255))
        # self.screen.blit(title_surf, (self.x + self.PADDING, self.y + 10))

        # Toggle Label
        toggle_label = label_font.render("One-Way System", True, self.TEXT_COLOR)
        self.screen.blit(toggle_label, (self.one_way_toggle.getX() - 100, self.one_way_toggle.getY() + 3))