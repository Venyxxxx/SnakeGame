# -*- coding: utf-8 -*-


import tkinter as tk
import random
import tkinter.messagebox as messagebox
import ctypes
import os
import sys

# Default sizes
DEFAULT_GRID_SIZE = 20
TILE_SIZE = 20
DEFAULT_MOVE_INTERVAL = "Normal"
HIGHSCORE_PATH = r"C:\Users\Kuruc Attila\source\repos\SnakeGame\SnakeGame"

HIGHSCORE_FILE = os.path.join(HIGHSCORE_PATH, "highscore.txt")


DIRECTIONS = {
    "w": (-1, 0),
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
}

COLOR_OPTIONS = {
    "blue": "#0000cc",
    "red": "#ff0000",
    "green": "#00cc00",
    "orange": "#ff9900",
    "lightblue": "#3399ff",
    "lightred": "#ff6666",
    "lightgreen": "#66ff66",
    "yellow": "#ffff66",
}

SPEED_OPTIONS = {
    "Slow": 500,
    "Normal": 300,
    "Fast": 200,
    "Very Fast": 100,
}

def resource_path(relative_path):
    """Adja vissza a forrásfájl/exe mappájához viszonyított teljes elérési utat."""
    try:
        # PyInstaller ide csomagolja a fájlokat
        base_path = sys._MEIPASS
    except Exception:
        # fejlesztési módban: a jelenlegi mappa
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#ffffff") #Bg color
        self.root.title("Snake Game")


        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"mycompany.mygame.snakegame")
        except Exception as e:
            print("Couldn't set the AppUserModelID:", e)

        # Game settings
        self.grid_size = DEFAULT_GRID_SIZE
        self.move_interval = SPEED_OPTIONS[DEFAULT_MOVE_INTERVAL]
        self.head_color_name = "blue"
        self.body_color_name = "lightblue"

        # Points
        self.score = 0
        self.high_score = 0

        # Highscore load from file
        self.load_highscore()

        # Control bar
        control_frame = tk.Frame(root, bg="#dddddd")
        control_frame.grid(row=0, column=0, sticky="ew")
        root.grid_columnconfigure(0, weight=1)

        #3 column
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=0)
        control_frame.grid_columnconfigure(2, weight=1)

        #Control frame
        center_controls = tk.Frame(control_frame, bg="#dddddd")
        center_controls.grid(row=0, column=1)

        tk.Label(center_controls, text="Speed:").pack(side="left", padx=2)
        self.speed_var = tk.StringVar(value=DEFAULT_MOVE_INTERVAL)
        speed_menu = tk.OptionMenu(center_controls, self.speed_var, *SPEED_OPTIONS.keys(), command=self.update_speed)
        speed_menu.pack(side="left")

        tk.Label(center_controls, text="Table size:").pack(side="left", padx=2)
        self.size_var = tk.IntVar(value=self.grid_size)
        size_menu = tk.OptionMenu(center_controls, self.size_var, 10, 15, 20, 25, 30, command=self.update_size)
        size_menu.pack(side="left")

        tk.Label(center_controls, text="Snake head:").pack(side="left", padx=2)
        self.head_color_var = tk.StringVar(value=self.head_color_name)
        head_color_menu = tk.OptionMenu(center_controls, self.head_color_var, *COLOR_OPTIONS.keys(), command=self.update_head_color)
        head_color_menu.pack(side="left")

        tk.Label(center_controls, text="Snake body:").pack(side="left", padx=2)
        self.body_color_var = tk.StringVar(value=self.body_color_name)
        body_color_menu = tk.OptionMenu(center_controls, self.body_color_var, *COLOR_OPTIONS.keys(), command=self.update_body_color)
        body_color_menu.pack(side="left")

        restart_btn = tk.Button(center_controls, text="Restart", command=self.restart_game)
        restart_btn.pack(side="left", padx=10)

        self.score_label = tk.Label(center_controls, text=f"Score: {self.score}   High Score: {self.high_score}")
        self.score_label.pack(side="left", padx=10)

        # Canvas frame
        canvas_frame = tk.Frame(root, bg="#b5e7a0")
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        root.grid_rowconfigure(1, weight=1)

        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(2, weight=1)

        self.canvas = tk.Canvas(canvas_frame,
                                width=self.grid_size * TILE_SIZE,
                                height=self.grid_size * TILE_SIZE,
                                bg="#b5e7a0")
        self.canvas.grid(row=0, column=1, pady=20)

        self.snake_squares = []  #Snake squares id's

        self.start_new_game()
        self.root.bind("<Key>", self.change_direction)

    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    self.high_score = int(f.read())
            except Exception:
                self.high_score = 0
        else:
            self.high_score = 0

    def save_highscore(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except Exception as e:
            print("Couldn't save highscore file:", e)

    def draw_grid(self):
        self.canvas.delete("grid")
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color = "#b5e7a0" if (row + col) % 2 == 0 else "#86af49"
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="grid")

    def start_new_game(self):
        self.snake = [(2, 4), (2, 3)]
        self.direction = "d"
        self.apple = None
        self.running = False
        self.score = 0
        self.update_score()
        self.place_apple()
        self.draw()

    def restart_game(self):
        self.running = False
        self.root.after(100, self.start_new_game)

    def update_speed(self, value):
        self.move_interval = SPEED_OPTIONS[value]
        self.restart_game()

    def update_size(self, value):
        self.grid_size = int(value)
        self.canvas.config(width=self.grid_size * TILE_SIZE, height=self.grid_size * TILE_SIZE)
        self.restart_game()

    def update_head_color(self, value):
        self.head_color_name = value
        self.restart_game()

    def update_body_color(self, value):
        self.body_color_name = value
        self.restart_game()

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()

        # Alma
        if self.apple:
            ar, ac = self.apple
            x1 = ac * TILE_SIZE
            y1 = ar * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE
            self.canvas.create_oval(x1+2, y1+2, x2-2, y2-2, fill="red", outline="black", width=2, tags="apple")

        # K�gy�
        for i, (r, c) in enumerate(self.snake):
            x1 = c * TILE_SIZE
            y1 = r * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE

            if i == 0:
                color = COLOR_OPTIONS.get(self.head_color_name, "#0000cc")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2, tags="snake")

                #Eyes
                eye_radius = TILE_SIZE // 6
                pupil_radius = eye_radius // 2
                eye_offset_x = TILE_SIZE // 4
                eye_offset_y = TILE_SIZE // 3

                eye1_x = x1 + eye_offset_x
                eye1_y = y1 + eye_offset_y
                self.canvas.create_oval(
                    eye1_x - eye_radius, eye1_y - eye_radius,
                    eye1_x + eye_radius, eye1_y + eye_radius,
                    fill="white", outline="black"
                )
                self.canvas.create_oval(
                    eye1_x - pupil_radius, eye1_y - pupil_radius,
                    eye1_x + pupil_radius, eye1_y + pupil_radius,
                    fill="black"
                )

                eye2_x = x1 + TILE_SIZE - eye_offset_x
                eye2_y = eye1_y
                self.canvas.create_oval(
                    eye2_x - eye_radius, eye2_y - eye_radius,
                    eye2_x + eye_radius, eye2_y + eye_radius,
                    fill="white", outline="black"
                )
                self.canvas.create_oval(
                    eye2_x - pupil_radius, eye2_y - pupil_radius,
                    eye2_x + pupil_radius, eye2_y + pupil_radius,
                    fill="black"
                )

            elif i == len(self.snake) - 1:
                color = COLOR_OPTIONS.get(self.body_color_name, "#66ff66")

                if len(self.snake) > 1:
                    r_prev, c_prev = self.snake[i - 1]
                else:
                    r_prev, c_prev = r, c

                dr = r - r_prev
                dc = c - c_prev

                cx = x1 + TILE_SIZE / 2
                cy = y1 + TILE_SIZE / 2
                size = TILE_SIZE // 2

                if dr == 1 and dc == 0:
                    points = [cx, cy + size, cx - size, cy - size, cx + size, cy - size]
                elif dr == -1 and dc == 0:
                    points = [cx, cy - size, cx - size, cy + size, cx + size, cy + size]
                elif dr == 0 and dc == 1:
                    points = [cx + size, cy, cx - size, cy - size, cx - size, cy + size]
                elif dr == 0 and dc == -1:
                    points = [cx - size, cy, cx + size, cy - size, cx + size, cy + size]
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2, tags="snake")
                    continue

                self.canvas.create_polygon(points, fill=color, outline="black", width=2, tags="snake")
            else:
                color = COLOR_OPTIONS.get(self.body_color_name, "#66ff66")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2, tags="snake")

    def change_direction(self, event):
        key = event.keysym.lower()
        if key in DIRECTIONS:
            opposite = {"w": "s", "s": "w", "a": "d", "d": "a"}
            if opposite[key] != self.direction:
                self.direction = key
            if not self.running:
                self.running = True
                self.auto_move()

    def auto_move(self):
        if not self.running:
            return
        self.move()
        self.root.after(self.move_interval, self.auto_move)

    def move(self):
        head_r, head_c = self.snake[0]
        dr, dc = DIRECTIONS[self.direction]
        new_r = head_r + dr
        new_c = head_c + dc
        new_head = (new_r, new_c)

        if not (0 <= new_r < self.grid_size and 0 <= new_c < self.grid_size):
            self.game_over("You hit the wall!")
            return

        if new_head in self.snake:
            self.game_over("You hit yourself!")
            return

        self.snake.insert(0, new_head)

        if self.apple and new_head == self.apple:
            self.score += 1
            self.update_score()
            self.place_apple()
        else:
            self.snake.pop()

        self.draw()

    def place_apple(self):
        empty_spaces = [
            (r, c)
            for r in range(self.grid_size)
            for c in range(self.grid_size)
            if (r, c) not in self.snake
        ]
        if not empty_spaces:
            self.game_over("Congrats! You filled the map!")
            return
        self.apple = random.choice(empty_spaces)

    def update_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_highscore()
        self.score_label.config(text=f"Score: {self.score}   High Score: {self.high_score}")

    def game_over(self, message):
        self.running = False
        self.update_score()
        messagebox.showinfo("Game Over", f"{message}\nScore: {self.score}\nHigh Score: {self.high_score}")
        self.restart_game()

root = tk.Tk()
game = SnakeGame(root)
root.mainloop()
