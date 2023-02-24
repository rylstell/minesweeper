import os.path
import pygame
import pygame.locals as pl
import json

pygame.init()



class Color:
    GRAY_50 = pygame.Color(50, 50, 50)
    GRAY_100 = pygame.Color(100, 100, 100)
    GRAY_150 = pygame.Color(150, 150, 150)
    GRAY_200 = pygame.Color(200, 200, 200)
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)
    RED = pygame.Color(255, 0, 0)
    RED_100 = pygame.Color(100, 0, 0)
    RED_200 = pygame.Color(200, 0, 0)
    GREEN = pygame.Color(0, 255, 0)
    GREEN_200 = pygame.Color(0, 200, 0)
    BLUE = pygame.Color(0, 0, 255)
    YELLOW = pygame.Color(255, 255, 0)






class Spritesheet:
    def __init__(self, sprites_filename, sprites_data_filename):
        self.surface = pygame.image.load(sprites_filename)
        self.data = json.load(open(sprites_data_filename))["frames"]

    def sprite(self, filename):
        xywh = self.data[filename]["frame"]
        return self.surface.subsurface(xywh["x"], xywh["y"], xywh["w"], xywh["h"])









class Signal:
    def __init__(self):
        self.func = None
    def connect(self, func):
        self.func = func
    def emit(self, *args, **kwargs):
        if self.func:
            self.func(*args, **kwargs)






class Widget:
    def __init__(self):
        self.display = True
    def set_display(self, display):
        self.display = display
    def check_event(self, event): pass
    def update(self, deltatime): pass
    def draw(self, surface): pass






class WidgetContainer:

    def __init__(self):
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def remove_widget(self, rm_widget):
        for i, widget in enumerate(self.widgets):
            if widget == rm_widget:
                self.widgets.pop(i)
                break

    def check_events(self, events):
        for event in events:
            for widget in self.widgets:
                if widget.display:
                    widget.check_event(event)

    def update(self, deltatime):
        for widget in self.widgets:
            if widget.display:
                widget.update(deltatime)

    def draw(self, surface):
        for widget in self.widgets:
            if widget.display:
                widget.draw(surface)







class RectWidget(Widget):

    def __init__(self, pos, center_draw):
        super().__init__()
        self.center_draw = center_draw
        self.rect = pygame.Rect((0,0), (0, 0))
        self.set_pos(pos)

    def set_pos(self, pos):
        if self.center_draw:
            self.rect.center = pos
        else:
            self.rect.topleft = pos

    def set_rect_size(self, size):
        if self.center_draw:
            pos = self.rect.center
            self.rect = pygame.Rect((0, 0), size)
            self.rect.center = pos
        else:
            pos = self.rect.topleft
            self.rect = pygame.Rect((0, 0), size)
            self.rect.topleft = pos









class Label(RectWidget):

    def __init__(self, pos, text="", center_draw=False):
        super().__init__(pos, center_draw)
        self.color = Color.WHITE
        self.font = pygame.font.SysFont("", 20)
        self.surfs = []
        self.surf_height = 0
        self.gap = 5
        self.set_text(text)

    def set_pos(self, pos):
        super().set_pos(pos)
        self.updated = True

    def set_gap(self, gap):
        self.gap = gap
        self.updated = True

    def set_text(self, text):
        self.text = text
        self.lines = str(text).split("\n")
        self.updated = True

    def set_color(self, color):
        self.color = color
        self.updated = True

    def set_font(self, name, size, sysfont=False):
        if sysfont:
            self.font = pygame.font.SysFont(name, size)
        else:
            self.font = pygame.font.Font(name, size)
        self.updated = True

    def get_text(self):
        return self.text

    def render_text(self):
        self.surfs = []
        w, h = 0, 0
        for line in self.lines:
            text_surf = self.font.render(line, True, self.color)
            rect = text_surf.get_rect()
            if rect.w > w: w = rect.w
            h += rect.h + self.gap
            self.surfs.append(text_surf)
        h -= self.gap
        self.surf_height = (h + self.gap) / len(self.surfs)
        self.set_rect_size((w, h))

    def update(self, deltatime):
        if self.updated:
            self.render_text()
            self.updated = False

    def draw(self, surface):
        x = self.rect.topleft[0]
        y = self.rect.topleft[1]
        for line in self.surfs:
            surface.blit(line, (x, y))
            y += self.surf_height







class AttrButton(Widget):
    def __init__(self, pos, text="Button"):
        super().__init__()
        self.text = text
        self.rect = pygame.Rect(pos, (1, 1))
        self.surface = pygame.Surface((1, 1))
        self.updated = True
        self.hovered = False
        self.clicked = Signal()
        self.attrs = {
            "border_color": Color.BLACK,
            "border_thickness": 3,
            "border_radius": 10,
            "background_color": Color.WHITE,
            "padding_left": 10,
            "padding_right": 10,
            "padding_top": 10,
            "padding_bottom": 10,
            "text_color": Color.BLACK,
            "text_font": pygame.font.Font("resources/consola.ttf", 14),
            "text_antialias": True,
            "hover_stuff": False
        }

    def set_attrs(self, attrs):
        self.updated = True
        for key, value in attrs.items():
            if key == "padding":
                self.attrs["padding_left"] = value
                self.attrs["padding_right"] = value
                self.attrs["padding_top"] = value
                self.attrs["padding_bottom"] = value
            elif key == "padding_horizontal":
                self.attrs["padding_left"] = value
                self.attrs["padding_right"] = value
            elif key == "padding_vertical":
                self.attrs["padding_top"] = value
                self.attrs["padding_bottom"] = value
            else:
                self.attrs[key] = value

    def click(self):
        self.clicked.emit()

    def check_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.click()

    def update(self, deltatime):
        if self.updated:
            self.updated = False
            self.render()

    def render(self):
        text_surface = self.attrs["text_font"].render(self.text, self.attrs["text_antialias"], self.attrs["text_color"])
        text_rect = text_surface.get_rect()
        topleft = self.rect.topleft
        self.rect = pygame.Rect(text_rect)
        self.rect.width += self.attrs["padding_left"] + self.attrs["padding_right"]
        self.rect.height += self.attrs["padding_top"] + self.attrs["padding_bottom"]
        self.surface = pygame.Surface(self.rect.size).convert_alpha()
        pygame.draw.rect(self.surface, self.attrs["background_color"], self.rect, border_radius=self.attrs["border_radius"])
        pygame.draw.rect(self.surface, self.attrs["border_color"], self.rect, width=self.attrs["border_thickness"], border_radius=self.attrs["border_radius"])
        text_rect.center = self.rect.center
        self.surface.blit(text_surface, text_rect.topleft)
        self.rect.topleft = topleft

    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)







class ButtonGroup(Widget):

    def __init__(self):
        super().__init__()
        self.buttons = WidgetContainer()
        self.btn_id = 0
        self.clicked = Signal()

    def add_button(self, button):
        id = self.btn_id
        self.btn_id += 1
        button.clicked.connect(lambda: self.btn_clicked(id))
        self.buttons.add_widget(button)

    def get_button(self, id):
        return self.buttons.widgets[id]

    def btn_clicked(self, id):
        self.clicked.emit(id)

    def check_event(self, event):
        self.buttons.check_events([event])

    def update(self, deltatime):
        self.buttons.update(deltatime)

    def draw(self, surface):
        self.buttons.draw(surface)






class Button(RectWidget):

    def __init__(self, pos, surface, hover_surface=None, center_draw=False):
        super().__init__(pos, center_draw)
        self.surface = surface
        self.hover_surface = hover_surface
        self.set_rect_size(self.surface.get_rect().size)
        self.draw_surface = self.surface
        self.hovered = False
        self.clicked = Signal()

    def click(self):
        self.clicked.emit()

    def contains_pt(self, pos):
        return self.rect.collidepoint(pos)

    def set_surface(self, surface):
        self.surface = surface
        self.set_rect_size(self.surface.get_rect().size)

    def check_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.click()
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.contains_pt(event.pos)

    def update(self, deltatime):
        if self.hover_surface and self.hovered:
            self.draw_surface = self.hover_surface
        else:
            self.draw_surface = self.surface

    def draw(self, surface):
        surface.blit(self.draw_surface, self.rect.topleft)







class TextInput(Widget):
    """
    This class lets the user input a piece of text, e.g. a name or a message.
    This class let's the user input a short, one-lines piece of text at a blinking cursor
    that can be moved using the arrow-keys. Delete, home and end work as well.
    """
    def __init__(
            self,
            image,
            pos=(0, 0),
            initial_string="",
            font_family="",
            font_size=35,
            antialias=True,
            text_color=(0, 0, 0),
            cursor_color=(0, 0, 1),
            repeat_keys_initial_ms=400,
            repeat_keys_interval_ms=35,
            max_string_length=-1,
            max_text_length=-1,
            text_offset=(0,0),
            focused_image=None):
        """
        :param initial_string: Initial text to be displayed
        :param font_family: name or list of names for font (see pygame.font.match_font for precise format)
        :param font_size:  Size of font in pixels
        :param antialias: Determines if antialias is applied to font (uses more processing power)
        :param text_color: Color of text (duh)
        :param cursor_color: Color of cursor
        :param repeat_keys_initial_ms: Time in ms before keys are repeated when held
        :param repeat_keys_interval_ms: Interval between key press repetition when held
        :param max_string_length: Allowed length of text
        """
        super().__init__()

        self.pos = pos

        # Text related vars:
        self.antialias = antialias
        self.text_color = text_color
        self.font_size = font_size
        self.max_string_length = max_string_length
        self.input_string = initial_string  # Inputted text

        if not os.path.isfile(font_family):
            font_family = pygame.font.match_font(font_family)

        self.font_object = pygame.font.Font(font_family, font_size)

        # Text-surface will be created during the first update call:
        self.text_surface = pygame.Surface((1, 1))
        self.text_surface.set_alpha(0)

        # Vars to make keydowns repeat after user pressed a key for some time:
        self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
        self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
        self.keyrepeat_interval_ms = repeat_keys_interval_ms

        # Things cursor:
        self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_size))
        self.cursor_surface.fill(cursor_color)
        self.cursor_position = len(initial_string)  # Inside text
        self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
        self.cursor_switch_ms = 500  # /|\
        self.cursor_ms_counter = 0

        if isinstance(image, pygame.Surface):
            self.unfocused_surface = image
            self.focused_surface = focused_image if focused_image else self.unfocused_surface
        else:
            self.unfocused_surface = pygame.image.load(image)
            self.focused_surface = pygame.image.load(focused_image) if focused_image else self.unfocused_surface
        self.bounding_surface = None
        self.focused = False
        self.bounding_rect = self.unfocused_surface.get_rect()
        self.max_text_length = max_text_length if max_text_length != -1 else self.bounding_rect.width
        self.bounding_rect.topleft = self.pos
        self.text_pos = (self.pos[0] + text_offset[0], self.pos[1] + text_offset[1])

        self.return_pressed = Signal()
        self.text_changed = Signal()

    def check_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.bounding_rect.collidepoint(event.pos)
            if not self.focused:
                self.keyrepeat_counters.clear()

        if not self.focused:
            return

        if event.type == pygame.KEYDOWN:

            self.cursor_visible = True  # So the user sees where he writes

            # If none exist, create counter for that key:
            if event.key not in self.keyrepeat_counters:
                self.keyrepeat_counters[event.key] = [0, event.unicode]

            if event.key == pl.K_BACKSPACE:
                prev_input_sting_len = len(self.input_string)
                self.input_string = (
                    self.input_string[:max(self.cursor_position - 1, 0)]
                    + self.input_string[self.cursor_position:]
                )
                # Subtract one from cursor_pos, but do not go below zero:
                self.cursor_position = max(self.cursor_position - 1, 0)
                if prev_input_sting_len != len(self.input_string):
                    self.text_changed.emit(self.input_string)

            elif event.key == pl.K_DELETE:
                prev_input_sting_len = len(self.input_string)
                self.input_string = (
                    self.input_string[:self.cursor_position]
                    + self.input_string[self.cursor_position + 1:]
                )
                if prev_input_sting_len != len(self.input_string):
                    self.text_changed.emit(self.input_string)

            elif event.key == pl.K_RETURN:
                self.return_pressed.emit()

            elif event.key == pl.K_RIGHT:
                # Add one to cursor_pos, but do not exceed len(input_string)
                self.cursor_position = min(self.cursor_position + 1, len(self.input_string))

            elif event.key == pl.K_LEFT:
                # Subtract one from cursor_pos, but do not go below zero:
                self.cursor_position = max(self.cursor_position - 1, 0)

            elif event.key == pl.K_END:
                self.cursor_position = len(self.input_string)

            elif event.key == pl.K_HOME:
                self.cursor_position = 0

            elif len(self.input_string) < self.max_string_length or self.max_string_length == -1:
                prev_input_sting_len = len(self.input_string)
                # If no special key is pressed, add unicode of key to input_string
                self.input_string = (
                    self.input_string[:self.cursor_position]
                    + event.unicode
                    + self.input_string[self.cursor_position:]
                )
                self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP
                if prev_input_sting_len != len(self.input_string):
                    self.text_changed.emit(self.input_string)

        elif event.type == pl.KEYUP:
            # *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
            if event.key in self.keyrepeat_counters:
                del self.keyrepeat_counters[event.key]

    def update(self, deltatime):
        # Update key counters:
        for key in self.keyrepeat_counters:
            self.keyrepeat_counters[key][0] += deltatime  # Update clock

            # Generate new key events if enough time has passed:
            if self.keyrepeat_counters[key][0] >= self.keyrepeat_intial_interval_ms:
                self.keyrepeat_counters[key][0] = (
                    self.keyrepeat_intial_interval_ms
                    - self.keyrepeat_interval_ms
                )

                event_key, event_unicode = key, self.keyrepeat_counters[key][1]
                pygame.event.post(pygame.event.Event(pl.KEYDOWN, key=event_key, unicode=event_unicode))

        # Re-render text surface:
        text = " " if len(self.input_string) == 0 else self.input_string
        self.text_surface = self.font_object.render(text, self.antialias, self.text_color)

        # Update self.cursor_visible
        self.cursor_ms_counter += deltatime
        if self.cursor_ms_counter >= self.cursor_switch_ms:
            self.cursor_ms_counter %= self.cursor_switch_ms
            self.cursor_visible = not self.cursor_visible

        if self.focused:
            self.bounding_surface = self.focused_surface
            if self.cursor_visible:
                cursor_x_pos = self.font_object.size(self.input_string[:self.cursor_position])[0]
                # Without this, the cursor is invisible when self.cursor_position > 0:
                if self.cursor_position > 0:
                    cursor_x_pos -= self.cursor_surface.get_width()
                self.text_surface.blit(self.cursor_surface, (cursor_x_pos, 0))
        else:
            self.bounding_surface = self.unfocused_surface

    def draw(self, surface):
        surface.blit(self.bounding_surface, self.pos)
        surface.blit(self.text_surface, self.text_pos)

    def get_surface(self):
        return self.text_surface

    def get_text(self):
        return self.input_string

    def get_cursor_position(self):
        return self.cursor_position

    def set_text_color(self, color):
        self.text_color = color

    def set_text(self, text):
        self.input_string = text
        self.cursor_position = len(self.input_string)

    def set_cursor_color(self, color):
        self.cursor_surface.fill(color)

    def clear_text(self):
        self.input_string = ""
        self.cursor_position = 0








class Scene(WidgetContainer):

    def __init__(self):
        super().__init__()
        self.set_background()
        self.windows = []

    def set_background(self, image_filename=None, surface=None, color=Color.BLACK, size=None):
        if image_filename:
            self.surface = pygame.image.load(image_filename)
            if size:
                self.surface = pygame.transform.scale(self.surface, size)
        elif surface:
            self.surface = surface
            if size:
                self.surface = pygame.transform.scale(self.surface, size)
        else:
            size = (400, 300) if not size else size
            self.surface = pygame.Surface(size)
            self.surface.fill(color)
        self.rect = self.surface.get_rect()

    def add_window(self, window):
        self.windows.append(window)

    def check_events(self, events):
        widget_container = self
        for event in events:
            for window in self.windows:
                if window.display:
                    if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                        if window.rect.collidepoint(event.pos):
                            widget_container = window
                    elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                        widget_container = window
        if widget_container == self:
            super().check_events(events)
        else:
            widget_container.check_events(events)

    def update(self, deltatime):
        super().update(deltatime)
        for window in self.windows:
            if window.display:
                window.update(deltatime)

    def draw(self, surface):
        surface.blit(self.surface, (0, 0))
        super().draw(surface)
        for window in self.windows:
            if window.display:
                window.draw(surface)





class Window(WidgetContainer):

    def __init__(self, pos):
        super().__init__()
        self.display = False
        self.pos = pos

    def set_background(self, surface):
        self.surface = surface
        self.rect = self.surface.get_rect()
        self.rect.topleft = self.pos

    def set_display(self, display):
        self.display = display

    def draw(self, surface):
        surface.blit(self.surface, self.pos)
        super().draw(surface)





class App:

    def __init__(self, size=(200, 200)):
        self.window = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.running = False
        self.scenes = {}
        self.current_scene = Scene()

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def set_scene(self, name):
        size = self.scenes[name].rect.size
        self.resize_window(size)
        self.current_scene = self.scenes[name]

    def scene(self, name):
        return self.scenes[name]

    def resize_window(self, size):
        self.window = pygame.display.set_mode(size)

    def _check_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def run(self):
        self.running = True
        while self.running:
            deltatime = self.clock.tick(self.fps)
            events = pygame.event.get()
            self._check_events(events)
            self.current_scene.check_events(events)
            self.current_scene.update(deltatime)
            self.current_scene.draw(self.window)
            pygame.display.update()
