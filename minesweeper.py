import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame
from enum import Enum
from random import randint
import json
from gui_stuff import *
import requests

pygame.init()

MSSPRITES = Spritesheet("resources/spritesheet.png", "resources/spritesheet.json")





class Timer:

    def __init__(self):
        self.time = 0
        self.start_ticks = 0
        self.on = False

    def start(self):
        self.on = True
        self.start_ticks = pygame.time.get_ticks() - self.time * 1000

    def stop(self):
        self.on = False

    def set_time(self, time):
        self.time = time
        self.start_ticks = pygame.time.get_ticks() - self.time * 1000

    def reset(self):
        self.time = 0
        self.start_ticks = 0
        self.on = False

    def update(self):
        if self.on:
            self.time = (pygame.time.get_ticks() - self.start_ticks) / 1000






class NumberTextInput(TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_changed.connect(lambda text: self.set_text("".join(filter(str.isnumeric, text))))





class UpperAlphaTextInput(TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_changed.connect(lambda text: self.set_text("".join(filter(str.isalpha, text.upper()))))






class MsDigitalDisplay(Label):

    def __init__(self, pos, num):
        super().__init__(pos, num)
        bg_border = 3
        self.bg_rect = pygame.Rect((self.rect.left, self.rect.top+5), (40, 22))
        self.bg_rect.inflate_ip(bg_border*2, bg_border*2)
        self.size_poss = [
            self.rect.topleft + pygame.Vector2(28, 0),
            self.rect.topleft + pygame.Vector2(14, 0),
            self.rect.topleft
        ]
        self.set_font("resources/digital.ttf", 32)
        self.set_color(Color.RED)
        self.set_number(num)

    def set_number(self, num):
        num = min(num, 999)
        i = len(str(num)) - 1
        self.set_pos(self.size_poss[i])
        self.set_text(num)

    def draw(self, surface):
        pygame.draw.rect(surface, Color.RED_100, self.bg_rect, border_radius=2)
        super().draw(surface)






class MsSmileyButton(Button):

    def __init__(self, pos, center_draw=False):
        super().__init__(pos, MSSPRITES.sprite("btn_smiley.png"), center_draw=center_draw)
        self.smilies = {
            "norm": self.surface,
            "won": MSSPRITES.sprite("btn_smiley_won.png"),
            "lost": MSSPRITES.sprite("btn_smiley_lost.png")
        }
        self.smile_surface = self.surface

    def set_smile(self, smile):
        self.smile_surface = self.smilies[smile]

    def draw(self, surface):
        self.draw_surface = self.smile_surface
        super().draw(surface)








class MsMenu(Scene):

    def __init__(self):
        super().__init__()

        self.btn_easy = Button((16, 140), MSSPRITES.sprite("btn_easy.png"), hover_surface=MSSPRITES.sprite("btn_easy_hover.png"))
        self.btn_medium = Button((112, 140), MSSPRITES.sprite("btn_medium.png"), hover_surface=MSSPRITES.sprite("btn_medium_hover.png"))
        self.btn_hard = Button((208, 140), MSSPRITES.sprite("btn_hard.png"), hover_surface=MSSPRITES.sprite("btn_hard_hover.png"))
        self.btn_custom = Button((304, 140), MSSPRITES.sprite("btn_custom.png"), hover_surface=MSSPRITES.sprite("btn_custom_hover.png"))
        self.btn_start = Button((160, 230), MSSPRITES.sprite("btn_start.png"), hover_surface=MSSPRITES.sprite("btn_start_hover.png"))
        self.btn_scores = Button((310, 265), MSSPRITES.sprite("btn_scores.png"), hover_surface=MSSPRITES.sprite("btn_scores_hovered.png"))

        self.label_diff = Label((220, 190), MsApp.Difficulty.EASY.name)
        self.label_diff.set_font("resources/consola.ttf", 24)
        self.label_diff.set_color(Color.GRAY_50)

        self.label_config = Label((10, 274))
        self.label_config.set_font("resources/consola.ttf", 14)
        self.label_config.set_color(Color.GRAY_50)

        self.add_widget(self.btn_easy)
        self.add_widget(self.btn_medium)
        self.add_widget(self.btn_hard)
        self.add_widget(self.btn_custom)
        self.add_widget(self.btn_start)
        self.add_widget(self.btn_scores)
        self.add_widget(self.label_diff)
        self.add_widget(self.label_config)

        self.set_background(surface=MSSPRITES.sprite("bg_menu.png"))

    def set_config_text(self, config):
        text = f"Rows: {config['num_rows']} | Cols: {config['num_cols']} | Mines: {config['num_mines']}"
        self.label_config.set_text(text)










class MsCustomMenu(Scene):

    def __init__(self):
        super().__init__()
        self.btn_menu = Button((10, 10), MSSPRITES.sprite("btn_menu.png"), hover_surface=MSSPRITES.sprite("btn_menu_hover.png"))
        self.btn_set_custom = Button((160, 230), MSSPRITES.sprite("btn_submit.png"), hover_surface=MSSPRITES.sprite("btn_submit_hover.png"))
        self.input_num_rows = NumberTextInput(MSSPRITES.sprite("text_input.png"), pos=(200, 70), max_string_length=3, text_offset=(10, 3), font_size=24, font_family="resources/digital.ttf", focused_image=MSSPRITES.sprite("text_input_focused.png"))
        self.input_num_cols = NumberTextInput(MSSPRITES.sprite("text_input.png"), pos=(200, 120), max_string_length=3, text_offset=(10, 3), font_size=24, font_family="resources/digital.ttf", focused_image=MSSPRITES.sprite("text_input_focused.png"))
        self.input_num_mines = NumberTextInput(MSSPRITES.sprite("text_input.png"), pos=(200, 170), max_string_length=3, text_offset=(10, 3), font_size=24, font_family="resources/digital.ttf", focused_image=MSSPRITES.sprite("text_input_focused.png"))
        self.label_error = Label((10, 275))
        self.label_error.set_font("resources/consola.ttf", 20)
        self.label_error.set_color(Color.GRAY_50)
        self.add_widget(self.btn_menu)
        self.add_widget(self.btn_set_custom)
        self.add_widget(self.input_num_rows)
        self.add_widget(self.input_num_cols)
        self.add_widget(self.input_num_mines)
        self.add_widget(self.label_error)
        self.set_background(surface=MSSPRITES.sprite("bg_custom_menu.png"))

    def get_config(self):
        return {
            "num_rows": self.input_num_rows.get_text(),
            "num_cols": self.input_num_cols.get_text(),
            "num_mines": self.input_num_mines.get_text()
        }

    def clear_inputs(self):
        self.input_num_rows.set_text("")
        self.input_num_cols.set_text("")
        self.input_num_mines.set_text("")
        self.label_error.set_text("")









class MsScoresMenu(Scene):

    def __init__(self):
        super().__init__()
        self.btn_menu = Button((10, 10), MSSPRITES.sprite("btn_menu.png"), hover_surface=MSSPRITES.sprite("btn_menu_hover.png"))
        self.label_easy = Label((20, 100))
        self.label_medium = Label((150, 100))
        self.label_hard = Label((275, 100))
        self.label_easy.set_color(Color.BLACK)
        self.label_medium.set_color(Color.BLACK)
        self.label_hard.set_color(Color.BLACK)
        self.label_easy.set_font("resources/consola.ttf", 12)
        self.label_medium.set_font("resources/consola.ttf", 12)
        self.label_hard.set_font("resources/consola.ttf", 12)
        self.add_widget(self.btn_menu)
        self.add_widget(self.label_easy)
        self.add_widget(self.label_medium)
        self.add_widget(self.label_hard)
        self.set_background(surface=MSSPRITES.sprite("bg_scores_menu.png"))









class MsCell:

    class State(Enum):
        NORM = 0
        REVEALED = 1
        NUMBERED = 2
        FLAGGED = 3
        REVEALED_MINE = 4
        REVEALED_MINE_X = 5
        REVEALED_MINE_RED = 6

    def __init__(self, i, j, state=State.NORM):
        self.i = i
        self.j = j
        self.state = state
        self.num_mines = -1
        self.mine = False









class Minesweeper:

    class State(Enum):
        START = 0
        PLAYING = 1
        WON = 2
        LOST = 3

    def __init__(self, rows, cols, total_mines):
        self.rows = rows
        self.cols = cols
        self.total_mines = total_mines
        self.active_cells = self.rows * self.cols
        self.mines_remaining = self.total_mines
        self.grid = [[MsCell(row, col) for col in range(self.cols)] for row in range(self.rows)]
        self.state = Minesweeper.State.START
        self.mines = []

    def left_click(self, row, col):
        cell = self.grid[row][col]
        if cell.state == MsCell.State.FLAGGED:
            return
        if self.state == Minesweeper.State.START:
            self.start_game(cell)
        if self.state == Minesweeper.State.PLAYING:
            self.reveal_cell(cell)

    def right_click(self, row, col):
        if self.state == Minesweeper.State.WON or self.state == Minesweeper.State.LOST:
            return
        cell = self.grid[row][col]
        if cell.state == MsCell.State.NORM:
            cell.state = MsCell.State.FLAGGED
            self.mines_remaining -= 1
        elif cell.state == MsCell.State.FLAGGED:
            cell.state = MsCell.State.NORM
            self.mines_remaining += 1

    def start_game(self, cell):
        self.place_random_mines(cell)
        self.set_mine_counts(self.grid[0][0])
        self.state = Minesweeper.State.PLAYING

    def are_neighbors(self, c1, c2):
        return abs(c1.i - c2.i) <= 1 and abs(c1.j - c2.j) <= 1

    def place_random_mines(self, first_cell):
        cells = set()
        while len(cells) < self.total_mines:
            i, j = randint(0, self.rows-1), randint(0, self.cols-1)
            rand_cell = self.grid[i][j]
            if not self.are_neighbors(first_cell, rand_cell):
                cells.add(rand_cell)
        for cell in cells:
            cell.mine = True
            self.mines.append(cell)

    def set_mine_counts(self, first_cell):
        first_cell.num_mines = 0
        for neighbor in self.get_neighbors(first_cell):
            if neighbor.mine:
                first_cell.num_mines += 1
            if neighbor.num_mines == -1:
                self.set_mine_counts(neighbor)

    def reveal_cell(self, cell):
        if cell.mine:
            cell.state = MsCell.State.REVEALED_MINE_RED
            self.game_lost()
        elif cell.state == MsCell.State.NORM:
            self.flood_reveal(cell)
            if self.game_is_won():
                self.game_won()

    def flood_reveal(self, cell):
        cell.state = MsCell.State.REVEALED
        q_cells = [cell]
        while q_cells:
            cell = q_cells.pop(0)
            self.active_cells -= 1
            if cell.num_mines:
                cell.state = MsCell.State.NUMBERED
                continue
            for neighbor in self.get_neighbors(cell):
                if neighbor.state == MsCell.State.NORM:
                    neighbor.state = MsCell.State.REVEALED
                    q_cells.append(neighbor)

    def reveal_all_mines(self):
        for cell in self.all_cells():
            if cell.state == MsCell.State.FLAGGED:
                if not cell.mine:
                    cell.state = MsCell.State.REVEALED_MINE_X
            elif cell.mine and cell.state == MsCell.State.NORM:
                cell.state = MsCell.State.REVEALED_MINE

    def all_cells(self):
        for row in self.grid:
            for cell in row:
                yield cell

    def get_neighbors(self, cell):
        for i in range(-1, 2):
            for j in range(-1, 2):
                ni = cell.i + i
                nj = cell.j + j
                if (ni < 0) or (ni > self.rows-1) or (nj < 0) or (nj > self.cols-1) or (i == 0 and j == 0):
                    continue
                neighbor = self.grid[ni][nj]
                yield neighbor

    def game_is_won(self):
        return self.active_cells == self.total_mines

    def flag_all_mines(self):
        for mine in self.mines:
            mine.state = MsCell.State.FLAGGED

    def game_won(self):
        self.state = Minesweeper.State.WON
        self.flag_all_mines()

    def game_lost(self):
        self.state = Minesweeper.State.LOST
        self.reveal_all_mines()









class MsWidget(Widget):

    SURFS = [
        MSSPRITES.sprite("cell_norm.png"),
        MSSPRITES.sprite("cell_revealed.png"),
        MSSPRITES.sprite("cell_revealed.png"),
        MSSPRITES.sprite("cell_flagged.png"),
        MSSPRITES.sprite("cell_revealed_mine.png"),
        MSSPRITES.sprite("cell_revealed_mine_x.png"),
        MSSPRITES.sprite("cell_revealed_mine_red.png")
    ]

    FONT = pygame.font.Font("resources/consola.ttf", 20)
    NUMBERS = [
        FONT.render("0", True, Color.BLACK),
        FONT.render("1", True, Color.BLACK),
        FONT.render("2", True, Color.BLACK),
        FONT.render("3", True, Color.BLACK),
        FONT.render("4", True, Color.BLACK),
        FONT.render("5", True, Color.BLACK),
        FONT.render("6", True, Color.BLACK),
        FONT.render("7", True, Color.BLACK),
        FONT.render("8", True, Color.BLACK)
    ]

    def __init__(self, rows, cols, mines, rect):
        super().__init__()
        self.ms = Minesweeper(rows, cols, mines)
        self.rect = rect
        self.cell_flagged = Signal()
        self.game_started = Signal()
        self.game_won = Signal()
        self.game_lost = Signal()

    def get_cell_location(self, pos):
        x, y = pos
        scale = self.rect.w / self.ms.cols
        row = int((y - self.rect.top) / scale)
        col = int((x - self.rect.left) / scale)
        return row, col

    def on_widget(self, pos):
        return self.rect.collidepoint(pos)

    def check_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.on_widget(event.pos):
                row, col = self.get_cell_location(event.pos)
                if event.button == 1:
                    self.left_click(row, col)
                elif event.button == 3:
                    self.right_click(row, col)

    def left_click(self, row, col):
        if self.ms.state == Minesweeper.State.WON or self.ms.state == Minesweeper.State.LOST:
            return
        prev_ms_state = self.ms.state
        self.ms.left_click(row, col)
        if self.ms.state == Minesweeper.State.START:
            return
        elif prev_ms_state == Minesweeper.State.START:
            self.game_started.emit()
        if self.ms.state == Minesweeper.State.WON:
            self.game_won.emit()
        elif self.ms.state == Minesweeper.State.LOST:
            self.game_lost.emit()

    def right_click(self, row, col):
        if self.ms.state == Minesweeper.State.WON or self.ms.state == Minesweeper.State.LOST:
            return
        self.ms.right_click(row, col)
        self.cell_flagged.emit(self.ms.mines_remaining)

    def draw(self, surface):
        x, y = self.rect.left, self.rect.top
        scale = self.rect.w / self.ms.cols
        for row in self.ms.grid:
            for cell in row:
                surface.blit(MsWidget.SURFS[cell.state.value], (x, y))
                if cell.state == MsCell.State.NUMBERED:
                    surface.blit(MsWidget.NUMBERS[cell.num_mines], (x+7, y+5))
                x += scale
            y += scale
            x = self.rect.left








class MsGameScene(Scene):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.border = 10
        self.scale = 25
        self.top_bar = 50
        self.size = (
            self.config["num_cols"] * self.scale + self.border * 2,
            self.config["num_rows"] * self.scale + self.border * 2 + self.top_bar
        )
        self.timer = Timer()
        self.init_ui()
        self.create_background()

    def init_ui(self):
        x_half = self.size[0] / 2
        pos1 = (20, 25)
        pos2 = (25 + (x_half-25) / 2 - 23, 9)
        pos3 = (x_half, 25)
        pos4 = (5 + x_half + (x_half-25) / 2 - 23, 9)
        widget_ms_rect = pygame.Rect((self.border, self.top_bar + self.border), (self.config["num_cols"] * self.scale, self.config["num_rows"] * self.scale))
        self.btn_return = Button(pos1, MSSPRITES.sprite("btn_return.png"), center_draw=True)
        self.label_mines_rem = MsDigitalDisplay(pos2, self.config["num_mines"])
        self.btn_reset = MsSmileyButton(pos3, center_draw=True)
        self.label_time = MsDigitalDisplay(pos4, 0)
        self.widget_ms = MsWidget(self.config["num_rows"], self.config["num_cols"], self.config["num_mines"], widget_ms_rect)
        self.widget_ms.cell_flagged.connect(self.widget_ms_cell_flagged)
        self.widget_ms.game_started.connect(self.widget_ms_game_started)
        self.widget_ms.game_won.connect(self.widget_ms_game_won)
        self.widget_ms.game_lost.connect(self.widget_ms_game_lost)
        self.add_widget(self.btn_return)
        self.add_widget(self.btn_reset)
        self.add_widget(self.label_mines_rem)
        self.add_widget(self.label_time)
        self.add_widget(self.widget_ms)
        self.create_window_record_score()

    def create_window_record_score(self):
        pos = (self.size[0] / 2 - 65, self.size[1] / 2 - 60)
        self.window_record_score = Window(pos)
        self.window_record_score.set_background(surface=MSSPRITES.sprite("score_window.png"))
        self.label_score = Label((pos[0]+72, pos[1]+10), "500")
        self.label_score.set_color(Color.BLACK)
        self.label_score.set_font("resources/consola.ttf", 24)
        self.input_name = UpperAlphaTextInput(MSSPRITES.sprite("text_input.png"), pos=(pos[0]+15, pos[1]+70), max_string_length=10, text_offset=(10, 9), font_size=14, font_family="resources/consola.ttf", focused_image=MSSPRITES.sprite("text_input_focused.png"))
        self.btn_submit_score = Button((pos[0]+25, pos[1]+112), MSSPRITES.sprite("btn_submit.png"), hover_surface=MSSPRITES.sprite("btn_submit_hover.png"))
        self.window_record_score.add_widget(self.label_score)
        self.window_record_score.add_widget(self.input_name)
        self.window_record_score.add_widget(self.btn_submit_score)
        self.add_window(self.window_record_score)

    def create_background(self):
        bg = pygame.Surface(self.size)
        bg.fill(Color.GRAY_200)
        rect = pygame.Rect(0, self.top_bar, self.size[0], self.size[1]-self.top_bar)
        x, y = 0, self.top_bar
        bands = 5
        for i in range(2):
            for j in range(bands):
                rect.topleft = x, y
                color = Color.GRAY_100.lerp(Color.WHITE, j / bands)
                pygame.draw.rect(bg, color, rect, width=1, border_radius=2)
                rect.inflate_ip(-2, -2)
                x, y = x + 1, y + 1
            rect = pygame.Rect(0, 0, self.size[0], self.top_bar)
            x, y = 0, 0
        self.set_background(surface=bg)

    def widget_ms_cell_flagged(self, mines_remaining):
        self.label_mines_rem.set_number(mines_remaining)

    def widget_ms_game_started(self):
        self.timer.set_time(1)
        self.timer.start()

    def widget_ms_game_won(self):
        self.btn_reset.set_smile("won")
        self.timer.stop()
        self.label_mines_rem.set_number(0)
        self.label_score.set_text(int(self.timer.time))
        self.window_record_score.set_display(True)

    def widget_ms_game_lost(self):
        self.btn_reset.set_smile("lost")
        self.timer.stop()

    def update(self, deltatime):
        self.timer.update()
        self.label_time.set_number(int(self.timer.time))
        super().update(deltatime)







class MsApp(App):

    class Difficulty(Enum):
        EASY = 0
        MEDIUM = 1
        HARD = 2
        CUSTOM = 3

    def __init__(self, config_file):
        super().__init__()
        self.config = json.load(open(config_file))
        self.difficulty = MsApp.Difficulty.EASY
        self.create_menu_scene()
        self.create_custom_scene()
        self.create_scores_scene()
        self.set_scene("menu")
        self.scene("menu").btn_easy.click()

    def create_menu_scene(self):
        menu_scene = MsMenu()
        menu_scene.btn_easy.clicked.connect(lambda: self.btn_diff_handler(MsApp.Difficulty.EASY))
        menu_scene.btn_medium.clicked.connect(lambda: self.btn_diff_handler(MsApp.Difficulty.MEDIUM))
        menu_scene.btn_hard.clicked.connect(lambda: self.btn_diff_handler(MsApp.Difficulty.HARD))
        menu_scene.btn_start.clicked.connect(self.btn_start_handler)
        menu_scene.btn_custom.clicked.connect(self.btn_custom_handler)
        menu_scene.btn_scores.clicked.connect(self.btn_scores_clicked)
        self.add_scene("menu", menu_scene)

    def create_custom_scene(self):
        custom_scene = MsCustomMenu()
        custom_scene.btn_menu.clicked.connect(self.btn_return_handler)
        custom_scene.btn_set_custom.clicked.connect(self.btn_set_custom_handler)
        self.add_scene("custom", custom_scene)

    def create_game_scene(self):
        game_scene = MsGameScene(self.config["diffs"][self.difficulty.value])
        game_scene.btn_return.clicked.connect(self.btn_return_handler)
        game_scene.btn_reset.clicked.connect(self.btn_reset_handler)
        game_scene.btn_submit_score.clicked.connect(self.btn_submit_score_clicked)
        self.add_scene("game", game_scene)

    def create_scores_scene(self):
        scores_scene = MsScoresMenu()
        scores_scene.btn_menu.clicked.connect(self.btn_return_handler)
        self.add_scene("scores", scores_scene)

    def btn_diff_handler(self, diff):
        self.difficulty = diff
        self.scene("menu").label_diff.set_text(diff.name)
        self.scene("menu").set_config_text(self.config["diffs"][diff.value])

    def btn_start_handler(self):
        self.create_game_scene()
        self.set_scene("game")

    def btn_custom_handler(self):
        self.scene("custom").clear_inputs()
        self.set_scene("custom")

    def btn_return_handler(self):
        self.set_scene("menu")

    def btn_reset_handler(self):
        self.create_game_scene()
        self.set_scene("game")

    def btn_scores_clicked(self):
        try:
            response = requests.get("http://api.ryanstella.me/minesweeper/high-score")
            scores = response.json()
            diffs = {"easy": [], "medium": [], "hard": []}
            for score in scores:
                if score["diff"] == "custom": continue
                diffs[score["diff"]].append((score["name"], score["score"]))
            diffs["easy"].sort(key=lambda score: score[1])
            diffs["medium"].sort(key=lambda score: score[1])
            diffs["hard"].sort(key=lambda score: score[1])
            easy_text = "\n".join([f"{name:{'.'}<12}{int(score)}" for name, score in diffs["easy"][:10]])
            medium_text = "\n".join([f"{name:{'.'}<12}{int(score)}" for name, score in diffs["medium"][:10]])
            hard_text = "\n".join([f"{name:{'.'}<12}{int(score)}" for name, score in diffs["hard"][:10]])
            self.scene("scores").label_easy.set_text(easy_text)
            self.scene("scores").label_medium.set_text(medium_text)
            self.scene("scores").label_hard.set_text(hard_text)
            self.set_scene("scores")
        except:
            pass

    def btn_set_custom_handler(self):
        config = self.scene("custom").get_config()
        if self.valid_config(config):
            self.difficulty = MsApp.Difficulty.CUSTOM
            self.config["diffs"][self.difficulty.value] = config
            self.scene("menu").set_config_text(config)
            self.scene("menu").label_diff.set_text(self.difficulty.name)
            self.set_scene("menu")
        else:
            self.scene("custom").label_error.set_text("INVALID INPUT NUMBERS")

    def btn_submit_score_clicked(self):
        name = self.scene("game").input_name.get_text()
        if len(name) < 3:
            return
        score = self.scene("game").timer.time
        diff = self.difficulty.name.lower()
        data = {"score": score, "name": name, "diff": diff}
        try:
            requests.post("http://api.ryanstella.me/minesweeper/high-score", data=data)
        except:
            pass
        self.scene("game").window_record_score.set_display(False)

    def valid_config(self, config):
        try:
            config["num_rows"] = int(config["num_rows"])
            config["num_cols"] = int(config["num_cols"])
            config["num_mines"] = int(config["num_mines"])
            too_many_mines = config["num_mines"] > config["num_rows"] * config["num_cols"] - 9
            if config["num_rows"] < 5 or config["num_cols"] < 5 or too_many_mines:
                return False
        except:
            return False
        return True










def main():

    pygame.display.set_caption("Minesweeper")
    pygame.display.set_icon(pygame.image.load("resources/icon.png"))

    ms = MsApp("resources/ms_config.json")
    ms.run()





if __name__ == "__main__":
    main()
