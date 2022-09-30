from tkinter import *
from math import floor
from random import choices
from random_text import random_text_sentences
from os.path import exists

acceptable_punct = ["period", "comma", "apostrophe", "quotedbl", "semicolon", "colon", "question", "greater", "less",
                    "bracketleft", "bracketright", "exclam", "at", "numbersign", "dollar", "percent", "asciicircum",
                    "ampersand", "asterisk", "parenleft", "parenright", "underscore", "minus", "plus", "equal",
                    "braceleft", "braceright", "backslash", "bar", "grave", "shift", "asciitilde", "slash"]


class App:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("900x300")
        self.window.resizable(False, False)
        self.window.title('Typing Speed Test')
        self.timer = None
        self.testing = False
        self.position = 0
        self.sec = 0
        self.correct_count = 0
        # --------------------------------------------Stats Display ------------------------------------------------ #
        self.wpm_label = Label(text="WPM:  0")
        self.wpm_label.place(relx=0.05, rely=0.07, anchor=W)
        self.accuracy_label = Label(text="Accuracy:   0%")
        self.accuracy_label.place(relx=0.3, rely=0.07, anchor=CENTER)
        self.timer_label = Label(text="Time: 00:00")
        self.timer_label.place(relx=0.5, rely=0.07, anchor=CENTER)
        avg, max_ = self.get_avg_hi_score()
        self.wpm_average_label = Label(text=f"WPM Avg: {avg}")
        self.wpm_average_label.place(relx=0.7, rely=0.07, anchor=CENTER)
        self.high_score_label = Label(text=f"High Score: {max_}")
        self.high_score_label.place(relx=0.95, rely=0.07, anchor=E)

        # -------------------------------------------- Text Field -------------------------------------------------- #
        sentences = choices(random_text_sentences, k=2)
        self.text = sentences[0] + sentences[1]
        self.entry_text = Text(height=6,
                               spacing2=10,
                               highlightthickness=0,
                               font=("Purisa", 22),
                               foreground='gray',
                               wrap=WORD,
                               width=60)
        self.entry_text.insert(INSERT, self.text)
        self.entry_text.place(relx=0.5, rely=0.45, anchor=CENTER)
        self.entry_text.mark_set("insert", "1.0")
        self.set_tags()
        self.entry_text.configure(state=DISABLED)
        self.cursor_position(self.position)
        # ------------------------------------------- Reset Button ------------------------------------------------- #
        self.reset_button = Button(text="Reset", command=self.reset)
        self.reset_button.place(relx=0.5, rely=0.88, anchor=CENTER)
        # --------------------------------------------Key Binding -------------------------------------------------- #
        self.window.bind('<Key>', self.next_character)
        # ---------------------------------------------------------------------------------------------------------- #
        self.window.mainloop()

    def start_timer(self):
        if not self.testing:
            self.count_up(self.sec)
            self.testing = True

    def stop_timer(self):
        self.window.after_cancel(self.timer)
        self.timer_label.configure(text="Time: 00:00")
        self.testing = False

    def count_up(self, count):
        self.timer = self.window.after(1000, self.count_up, count + 1)
        timer_sec = count % 60
        timer_min = floor(count / 60)
        if timer_sec < 10:
            timer_sec = f"0{timer_sec}"  # Add 0 in front of single digit seconds
        if timer_min < 10:
            timer_min = f"0{timer_min}"  # Add 0 in front of single digit minutes
        self.timer_label.configure(text=f"Time: {timer_min}:{timer_sec}")
        self.sec += 1

    def reset(self):
        sentences = choices(random_text_sentences, k=2)
        self.text = sentences[0] + sentences[1]

        self.entry_text.configure(state=NORMAL)
        self.entry_text.delete("1.0", END)
        self.entry_text.insert(INSERT, self.text)
        for tag in self.entry_text.tag_names():
            self.entry_text.tag_delete(tag)
        self.set_tags()
        self.entry_text.configure(state=DISABLED)

        self.sec = 0
        self.position = 0
        self.correct_count = 0
        self.cursor_position(self.position)

        if self.timer:
            self.stop_timer()

    def set_tags(self):
        self.entry_text.tag_configure("white", foreground="white", underline=False)
        self.entry_text.tag_configure("green", foreground="green", underline=False, underlinefg="green")
        self.entry_text.tag_configure("red", foreground="red", underline=False, underlinefg="red")
        self.entry_text.tag_configure("space", underline=True)
        self.replace_space_characters()

    def cursor_position(self, i):
        self.entry_text.configure(state=NORMAL)
        self.entry_text.mark_set('insert', f'1.{i}')  # Move insert cursor, useful for knowing position
        self.entry_text.tag_add('white', f'1.{i}', f'1.{i + 1}')
        self.entry_text.configure(state=DISABLED)

    def correct_key_press(self, i):
        self.correct_count += 1
        self.entry_text.configure(state=NORMAL)
        self.entry_text.tag_add('green', f'1.{i}', f'1.{i + 1}')
        self.entry_text.configure(state=DISABLED)

    def incorrect_key_press(self, i):
        self.entry_text.configure(state=NORMAL)
        self.entry_text.tag_add('red', f'1.{i}', f'1.{i + 1}')
        self.entry_text.configure(state=DISABLED)

    def replace_space_characters(self):  # Rework index notation
        for i in range(int(self.entry_text.index('1.end').split('.')[-1])):
            text_char = self.entry_text.get(f"1.{i}", f"1.{i + 1}")
            if text_char == " ":
                self.entry_text.tag_add("space", f"1.{i}", f"1.{i + 1}")

    def next_character(self, event):
        if self.entry_text.index(INSERT) == self.entry_text.index('1.end - 1c'):     # Check if at end of text
            self.sec -= 1  # self.sec adds one at the start of every second, so it's always ahead one second
            self.calculate_wpm()
            self.reset()
        elif event.char == event.keysym or event.keysym == "space" or event.keysym in acceptable_punct:
            text_char = self.entry_text.get(f"1.{self.position}", f"1.{self.position + 1}")     # Change to tkinter not
            if event.char == text_char:  # Check if correct key is pressed
                self.correct_key_press(self.position)
            else:
                self.incorrect_key_press(self.position)
            self.position += 1
            if self.position > 0:  # Start Timer if at first character
                self.start_timer()
            self.cursor_position(self.position)

    def calculate_wpm(self):
        char_count = len(self.entry_text.get("1.0", "1.end"))
        accuracy = round(self.correct_count / char_count * 100, 2)
        minutes = self.sec / 60
        adjusted_wpm = round(self.correct_count / (5 * minutes), 1)
        with open("data.txt", "a") as file:
            file.write(str(adjusted_wpm) + "\n")
        average_wpm, max_wpm = self.get_avg_hi_score()
        self.update_stats(accuracy, adjusted_wpm, average_wpm, max_wpm)

    def update_stats(self, acc, wpm, avg, max_):
        self.wpm_label.configure(text=f"WPM: {wpm}")
        self.accuracy_label.configure(text=f"Accuracy: {acc}%")
        self.wpm_average_label.configure(text=f"WPM Avg: {avg}")
        self.high_score_label.configure(text=f"High Score: {max_}")

    def get_avg_hi_score(self):
        if exists("data.txt"):
            with open("data.txt", "r") as file:
                data = file.readlines()
            previous_wpms = []
            for val in data:
                previous_wpms.append(float(val.replace("\n", "")))
            avg_wpm = round(sum(previous_wpms) / len(previous_wpms), 1)
            max_wpm = max(previous_wpms)
            return avg_wpm, max_wpm


app = App()
