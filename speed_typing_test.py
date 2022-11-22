import os
import json
import tkinter as tk
from tk_ui_helper_functions import set_window_position
from speed_test import SpeedTest

THEME_COLOR = "#375362"
DEFAULT_FONT = ("Times", 20, "normal")
ENTRY_FONT = ("Times", 18, "normal")
LARGE_FONT = ("Ariel", 30, "normal")
SMALL_FONT = ("Ariel", 14, "normal")
MIN_WIDTH = 600
MIN_HEIGHT = 600
DEFAULT_TITLE = "Speed Typing Tester"
DEFAULT_WINDOW_POSITION = "center"
BASE_PADDING = 50
NUM_STARTING_WORDS = 20
TEST_TIME = 60


class SpeedTypingTest:
    abs = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, **kw):
        # BASE SET UP:
        self.win = tk.Tk()
        self.width = kw.get("width") if kw.get("width") and kw.get("width") >= MIN_WIDTH else MIN_WIDTH
        self.height = MIN_HEIGHT if self.width <= MIN_WIDTH + 50 else self.width - 50
        self.title = kw.get("title") or DEFAULT_TITLE
        self.win_pos = kw["position"] if kw.get("position") else DEFAULT_WINDOW_POSITION
        self.pos = set_window_position(tk=self.win, width=self.width, height=self.height, position=self.win_pos)
        self.win.geometry(self.pos)
        self.win.title(self.title)
        self.win.config(bg=THEME_COLOR, padx=BASE_PADDING, pady=(BASE_PADDING // 4))
        self.win.resizable(False, False)

        # GAME SET UP:
        try:
            with open('high_score.json') as file:
                hs = json.load(file)
                self.current_best_cpm = hs['cpm']
                self.current_best_wpm = hs['wpm']
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.current_best_cpm = 0
            self.current_best_wpm = 0
        self.game = SpeedTest(NUM_STARTING_WORDS)
        self.current_word = ""
        self.current_user_word = ""
        self.current_game = {}
        self.timer = None
        self._game_reset(init=True)
        # UI SET UP:
        self._set_canvas()
        self._set_labels()
        self._set_buttons()
        self._set_entries()
        self._render_widgets()
        self.run()
        self.win.mainloop()

    # ------------------------- FUNCTIONALITY ------------------------- #

    def _game_reset(self, init: bool = False):
        if self.timer:
            self.win.after_cancel(self.timer)
        if not init:
            self.game.reset_words()
            self.restart_btn.grid(row=0, column=1, pady=(20, 1), ipadx=10, ipady=5)
            self.restart_btn.config(text="reset")
            self.word_label.config(text=f"Timer begins when you start typing.")
            self.canvas.itemconfig(self.results_text, text="")
            self.canvas.itemconfig(self.info_text, text="Type word and press the space bar."
                                                        "\n----------------------------------")
            self.current_score_label.config(text=f"Current Score: 0cpm (0wpm)")
        self.current_word = self.game.current_word
        self.current_user_word = ""
        self.current_game = {"correct_words": [],
                             "wrong_words": [],
                             "total_words": 0,
                             "total_chars": 0,
                             "total_words_true": 0,
                             "total_chars_true": 0,
                             "cpm": 0,
                             "wpm": 0,
                             "cpm_true": 0,
                             "wpm_true": 0,
                             "started": False,
                             "timer": TEST_TIME
                             }

    def _timer(self, count: int):
        if self.current_game['started']:
            timer = count % 60
            self.current_game['timer'] = timer
            timer = f"0{timer}" if timer < 10 else timer
            self.title_label.config(text=f"Speed Typing Test:   {timer}s")
        if count > 0:
            self.timer = self.win.after(1000, self._timer, count - 1)
        else:
            self._end_game()

    def run(self):
        self.reset_btn.grid_forget()
        self.title_label.config(text=f"Speed Typing Test:   {TEST_TIME}s")
        self.canvas.config(bg="#f4f07f")
        self.word_label.grid(row=4, column=0, columnspan=3, sticky=tk.E + tk.W, ipady=10, pady=(10, 0))
        self.text_entry['state'] = 'normal'
        self._update_page()
        self.text_entry.bind("<Key>", self.key_down)
        self.text_entry.bind("<BackSpace>", self.key_delete)
        self.text_entry.bind("<Return>", self.key_return)

    def key_down(self, key):
        if not self.current_game.get("started"):
            self._timer(TEST_TIME)
            self.current_game["started"] = True
            self.restart_btn.config(text="Restart")
            self.word_label.config(text=f"Current Word: {self.current_word}")
        if key.char == " ":
            self._change_word()
        else:
            self.current_user_word += key.char
            self._check_progress()

    def key_delete(self, key):
        if self.current_user_word:
            self.current_user_word = self.current_user_word[:len(self.current_user_word) - 1]
        self._check_progress()

    def key_return(self, key):
        self._change_word()

    def _change_word(self):
        self._update_current_game()
        self.current_word = self.game.get_next_word()
        if not self.current_word:
            self.game.reset_words()
            self.current_word = self.game.current_word
        self._update_page()

    def _check_progress(self):
        if len(self.current_user_word) <= 0:
            self.canvas.config(bg="#f4f07f")
        elif self.current_user_word == self.current_word[:len(self.current_user_word)]:
            self.canvas.config(bg="#7af4ad")
        else:
            self.canvas.config(bg="#f99090")

    def _update_current_game(self):
        if self.current_word == self.current_user_word:
            self.current_game['correct_words'].append(self.current_word)
            self.current_game['total_words'] += 1
            self.current_game['total_chars'] += len(self.current_word)
        else:
            self.current_game['wrong_words'].append(self.current_word)
        self.canvas.config(bg="#f4f07f")
        self.current_game['total_words_true'] += 1
        self.current_game['total_chars_true'] += len(self.current_word)
        self._calc_score()

    def _update_page(self):
        self.current_user_word = ""
        if self.current_game["started"]:
            self.word_label.config(text=f"Current Word: {self.current_word}")
        self.text_entry.delete(0, "end")
        words = ", ".join([f"[{word.upper()}]" if word == self.current_word else word for word in self.game.words])
        self.canvas.itemconfig(self.canvas_text, text=words)

    def _calc_score(self):
        if self.current_game['total_chars_true']:
            calc_words = self.current_game['total_chars'] // 5
            calc_words_true = self.current_game['total_chars_true'] // 5
            timer = (TEST_TIME - self.current_game['timer']) if (TEST_TIME - self.current_game['timer']) > 0 else 1
            self.current_game['cpm_true'] = int((self.current_game['total_chars_true'] / timer) * 60)
            self.current_game['cpm'] = int((self.current_game['total_chars'] / timer) * 60)
            self.current_game['wpm_true'] = int((calc_words_true / timer) * 60)
            self.current_game['wpm'] = int((calc_words / timer) * 60)
            self.current_score_label.config(
                text=f"Current Score: {self.current_game['cpm']}cpm ({self.current_game['wpm']}wpm)")

    def _end_game(self):
        self.current_game['game_over'] = True
        self.current_game["started"] = False
        self.text_entry['state'] = 'disabled'
        self.restart_btn.grid_forget()
        self.text_entry.unbind("<Key>")
        self.text_entry.unbind("<BackSpace>")
        self.word_label.grid_forget()
        self.reset_btn.grid(row=4, column=0, columnspan=3, sticky=tk.E + tk.W, ipady=10, pady=(10, 0))
        if self.current_game['wpm'] > self.current_best_wpm:
            self.current_best_wpm = self.current_game['wpm']
            self.current_best_cpm = self.current_game['cpm']
            best = f"High Score: {self.current_best_cpm}cpm ({self.current_best_wpm}wpm)"
            self.current_high_label.config(text=best)
            with open("high_score.json", "w") as file:
                json.dump(self.current_game, file)
        self._display_results()

    def _display_results(self):
        self.canvas.config(bg="#f4f07f")
        self.canvas.itemconfig(self.canvas_text, text="")
        self.canvas.itemconfig(self.info_text, text="")
        high_score = " - New High Score!" if self.current_game['wpm'] == self.current_best_wpm else ""
        possible = "" if len(self.current_game['wrong_words']) == 0 else f"You got " \
                   f"{len(self.current_game['wrong_words'])} word(s) wrong.\nyou could have had a score of: " \
                   f"{self.current_game['cpm_true']}cpm ({self.current_game['wpm_true']}wpm)"
        results = f"Time Up\n-------\n\nYou scored: {self.current_game['cpm']}cpm ({self.current_game['wpm']}wpm)" \
                  f"{high_score}\n\nYou correctly typed {self.current_game['total_words']} words\n\n{possible}" \
                  f"\n\nClick below to try again."
        self.canvas.itemconfig(self.results_text, text=results)

    def button_method(self):
        self._game_reset()
        self.run()

    # ------------------------- TK UI ------------------------- #

    @staticmethod
    def on_enter(e):
        e.widget.config(highlightbackground='#3e8abc', fg='black')

    @staticmethod
    def on_leave(e):
        e.widget.config(highlightbackground=THEME_COLOR, fg='black')

    def _set_canvas(self) -> None:
        # CREATE:
        canvas_width = self.width - (BASE_PADDING * 2)
        canvas_height = (canvas_width // 2)
        self.canvas = tk.Canvas(width=canvas_width, height=canvas_height, bg="#f4f07f")
        self.results_canvas = tk.Canvas(width=canvas_width, height=canvas_height)
        # CONFIGURE:
        x = canvas_width // 2
        y = canvas_height // 2
        self.canvas_text = self.canvas.create_text(x, y, text="", fill="#000", width=canvas_width, font=DEFAULT_FONT)
        self.results_text = self.canvas.create_text(x, y, text="", fill="#000", width=canvas_width, font=SMALL_FONT)
        self.info_text = self.canvas.create_text(x, y // 4, text="Type word and press the space bar."
                                                                 "\n----------------------------------",
                                                 fill="#000", width=canvas_width, font=SMALL_FONT)
        self.canvas.itemconfig(self.canvas_text, width=canvas_width - 40)
        self.canvas.itemconfig(self.results_text, width=canvas_width - 40, justify="center")
        self.canvas.itemconfig(self.info_text, width=canvas_width - 40, justify="center")

    def _set_labels(self) -> None:
        # CREATE:
        self.title_label = tk.Label(self.win, text=f"Speed Typing Test:   {TEST_TIME}s", font=LARGE_FONT)
        self.word_label = tk.Label(self.win, text=f"Timer begins when you start typing.", font=DEFAULT_FONT)
        best = f"High Score: {self.current_best_cpm}cpm ({self.current_best_wpm}wpm)"
        self.current_high_label = tk.Label(self.win, text=best, font=SMALL_FONT)
        self.current_score_label = tk.Label(self.win, text="Current Score: 0cpm (0wpm)", font=SMALL_FONT)
        # CONFIGURE:
        self.title_label.config(bg=THEME_COLOR, fg="white", bd=4)
        self.current_high_label.config(bg=THEME_COLOR, fg="white", bd=4)
        self.current_score_label.config(bg=THEME_COLOR, fg="white", bd=4)
        self.word_label.config(bg="#32434c", fg="white")

    def _set_buttons(self) -> None:
        # CREATE:
        self.reset_btn = tk.Button(text="Play Again", highlightthickness=0, command=self.button_method)
        self.restart_btn = tk.Button(text="Reset", highlightthickness=0, command=self.button_method)
        # # CONFIGURE:
        self.reset_btn.config(bg="blue", highlightbackground="blue", fg="black", font=DEFAULT_FONT)
        self.restart_btn.config(bg=THEME_COLOR, highlightbackground=THEME_COLOR, fg="black", font=SMALL_FONT)
        self.reset_btn.bind("<Enter>", self.on_enter)
        self.reset_btn.bind("<Leave>", self.on_leave)
        self.restart_btn.bind("<Enter>", self.on_enter)
        self.restart_btn.bind("<Leave>", self.on_leave)

    def _set_entries(self) -> None:
        # CREATE:
        self.input_var = tk.StringVar()
        self.text_entry = tk.Entry(textvariable=self.input_var, justify="center", font=ENTRY_FONT, bg="#6fa8c4")
        # CONFIGURE:
        self.text_entry.focus()

    def _render_widgets(self) -> None:
        self.current_high_label.grid(row=0, column=0, sticky=tk.W, pady=(20, 1))
        self.restart_btn.grid(row=0, column=1, pady=(20, 1), ipadx=10, ipady=5)
        self.current_score_label.grid(row=0, column=2, sticky=tk.E, pady=(20, 1))
        self.title_label.grid(row=1, column=0, columnspan=3, sticky=tk.E + tk.W, ipady=20)
        self.canvas.grid(row=2, column=0, columnspan=3)
        self.text_entry.grid(row=3, column=0, columnspan=3, sticky=tk.E + tk.W, pady=20, ipady=10)
        self.word_label.grid(row=4, column=0, columnspan=3, sticky=tk.E + tk.W, ipady=20, pady=(10, 0))
        self.canvas.grid_rowconfigure(0, weight=1)
