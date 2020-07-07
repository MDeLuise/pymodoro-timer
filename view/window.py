import threading
import time
import tkinter as tk
from tkinter import Label, Entry, StringVar, W, E, END


class SettingsW():

    def __init__(self, settings, main_window):
            super().__init__()
            self._settings = settings
            self._main_window = main_window
            t = threading.Thread(target = self._start_GUI)
            t.start()
            time.sleep(1) # needed to create GUI before Controller start


    def _start_GUI(self):
            self._root = tk.Tk()
            self._root.resizable(False, False)
            self._root.title("Settings")

            # form and label
            validation = self._root.register(self._only_numbers)

            canvas = tk.Canvas(self._root, height=250, width=500)
            canvas.pack()
            frame = tk.Frame(self._root, bg="#263D42")
            frame.place(relwidth=250, relheight=500)

            labelText = Label(frame, text="Work [seconds]:", font="none 20")
            labelText.grid(row=1, column=1, sticky=W, padx=(0,25))

            directory = StringVar(None)
            self._work = Entry(frame, textvariable=directory, validate="key",
                validatecommand=(validation, '%S'), width=4, font="none 20")
            self._work.grid(row=1, column=2, sticky=W)
            self._work.insert(END, str(self._settings["work"]))

            labelText1 = Label(frame, text="Short break [seconds]:",font="none 20")
            labelText1.grid(row=2, column=1, sticky=W, padx=(0,25))

            directory1 = StringVar(None)
            self._short = Entry(frame, textvariable=directory1, validate="key",
                validatecommand=(validation, '%S'), width=4, font="none 20")
            self._short.grid(row=2, column=2, sticky=W)
            self._short.insert(END, str(self._settings["short"]))

            labelText2 = Label(frame, text="Long break [seconds]:",font="none 20")
            labelText2.grid(row=3, column=1, sticky=W, padx=(0,25))

            directory2 = StringVar(None)
            self._long = Entry(frame, textvariable=directory2, validate="key",
                validatecommand=(validation, '%S'), width=4, font="none 20")
            self._long.grid(row=3, column=2, sticky=W)
            self._long.insert(END, str(self._settings["long"]))

            labelText3 = Label(frame, text="Pomodoro per round:",font="none 20")
            labelText3.grid(row=4, column=1, sticky=W, padx=(0,25))

            directory3 = StringVar(None)
            self._pom = Entry(frame, textvariable=directory3, validate="key",
                validatecommand=(validation, '%S'), width=4, font="none 20")
            self._pom.grid(row=4, column=2, sticky=W)
            self._pom.insert(END, str(self._settings["pom"]))


            # bottoms
            ok_btn = tk.Button(frame, text="Ok", padx=10,
                pady=5, fg="white", bg="#263D42", command=self._save_settings)
            ok_btn.grid(row=5, column=1, padx=6, sticky=E, pady=(15,0))

            cancel_btn = tk.Button(frame, text="Cancel", padx=10,
                pady=5, fg="white", bg="#263D42", command=self._root.destroy)
            cancel_btn.grid(row=5, column=2, padx=6, pady=(15,0))


            # start view
            self._root.protocol('WM_DELETE_WINDOW', self._root.destroy)
            self._root.mainloop()


    def _only_numbers(self, char):
        return char.isdigit()


    def _save_settings(self):
        self._main_window.save_settings({
            "work": int(self._work.get()),
            "short": int(self._short.get()),
            "long": int(self._long.get()),
            "pom": int(self._pom.get())
            })
        self._main_window.restart()
        self._root.destroy()