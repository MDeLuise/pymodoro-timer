from abc import ABC, abstractmethod
import os, sys
import threading
import time
import subprocess
import tkinter as tk
from tkinter import Text, Scrollbar, RIGHT, LEFT, CENTER, BOTH, Y, Listbox, Label, END, TOP, YES, Menu
from view.window import SettingsW



class View(ABC):

    def __init__(self, notify):
        self._notify = notify
        # "True" because if "False" congrats are printed even at first pomodoro
        self._congrats_printed = True

    @abstractmethod
    def print(self, state):
        pass

    @abstractmethod
    def update_time(self, time_state):
        pass

    def link_controller(self, controller):
        self._controller = controller

    def _notify_message(self, message):
        if self._notify:
            subprocess.Popen(['notify-send', message])

    def _notify_message_icon(self, message, icon):
        if self._notify:
            subprocess.Popen(['notify-send', '-i', icon, message])

    def _notify_message_title(self, message):
        if self._notify:
            subprocess.Popen(['notify-send', "Pomodoro timer", message])

    def _notify_message(self, message, icon):
        if self._notify:
            subprocess.Popen(['notify-send', "Pomodoro timer", '-i', icon, message])




class CLI(View):

    def __init__(self, notify):
        super().__init__(notify)
        print("### Insert a cmd (pause/resume/next/stop)")
        self._start_cmd_listener()


    def update_time(self, time_state):
        pass


    def print(self, state):
        self._notify_message_title(str(state["state"]))
        print("### " + str(state["state"]), end='')
        if state["pom"] == 0 and not self._congrats_printed:
            print(" [Pomodoroooo!]")
            self._congrats_printed = True
        else:
            # Can ben seen as:
            # "state['pom'] working phases are already FULLY done in this round".
            # So, (state['pom'] + 1) is the current phase.
            print(f" [Current: {state['pom'] + 1} of {state['pom_set']}]")
            if state["pom"] != 0: # if no this if: congrats at pause in first pomodoro
                self._congrats_printed = False


    def _start_cmd_listener(self):
        t = threading.Thread(target=self._listen_cmd)
        t.start()


    def _listen_cmd(self):
        try:
            cmd = input()
        except EOFError:
            time.sleep(2)
            self._start_cmd_listener()
            return

        if cmd == "pause" or cmd == "resume":
            self._controller.pause_or_resume()
        elif cmd == "next":
            self._controller.next()
        elif cmd == "stop":
            self._controller.stop()
            return
        else:
            print("Eh?")

        time.sleep(2)
        self._listen_cmd()



class GUI(View):
    def __init__(self, notify):
        super().__init__(notify)
        threading.Thread(target=self._start_GUI).start()
        time.sleep(1) # needed to create GUI before Controller start


    def _start_GUI(self):
        self._root = tk.Tk()
        self._root.resizable(False, False)
        self._root.title("Pomodoro timer")
        
        canvas = tk.Canvas(self._root, height=700, width=700, bg="#263D42")
        canvas.pack()

        self._create_top_frame()
        self._create_middle_frame()
        self._create_bottom_frame()

        self._create_menu()

        self._root.bind("<space>", lambda _: self._pause_or_resume())
        self._root.bind("<Control-q>", lambda _: self._stop_controller())
        self._root.bind("<Control-Right>", lambda _: self._next())


        self._root.protocol('WM_DELETE_WINDOW', self._exit_app)

        self._root.mainloop()


    def update_time(self, time_state):
        self._timer_lbl["text"] = f"{time_state['min']:02d}:{time_state['sec']:02d}"


    def print(self, state):
        self._notify_message_title(str(state["state"]))
        self._write_in_scrollbar(str(state["state"]))
        self._status_lbl["text"] = state["state"].time_label
        self._pomodoro_lbl["text"] = f"Current: {state['pom'] + 1} of {state['pom_set']}"


    def _create_top_frame(self):
        top_frame = tk.Frame(self._root, bg="white")
        top_frame.place(relwidth=0.8, relheight=0.47, relx=0.1, rely=0.05)

        self._status_lbl = Label(top_frame, text="", font="none 24 bold")
        self._status_lbl.config(anchor=CENTER)
        self._status_lbl.pack(side=TOP, expand=YES, fill=BOTH)

        self._timer_lbl = Label(top_frame, text="", font="none 30 bold")
        self._timer_lbl.config(anchor=CENTER)
        self._timer_lbl.pack(side=TOP, expand=YES, fill=BOTH)

        self._pomodoro_lbl = Label(top_frame, text="Current: 1 of ?", font="none 20 bold")
        self._pomodoro_lbl.config(anchor=CENTER)
        self._pomodoro_lbl.pack(side=TOP, expand=YES, fill=BOTH)
    

    def _create_middle_frame(self):
        self._middle_frame = tk.Frame(self._root, bg="white")
        self._middle_frame.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.59)
        scrollbar = Scrollbar(self._middle_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        self._text_list = Listbox(self._middle_frame, yscrollcommand=scrollbar.set)
        self._text_list.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self._text_list.yview)


    def _create_bottom_frame(self):
        self._bottom_frame = tk.Frame(self._root, bg="#263D42")
        self._bottom_frame.place(relwidth=0.8, relheight=0.1, relx=0.1, rely=0.87)
        self._create_buttons(self._root)
    

    def _create_menu(self):
        menubar = Menu(self._root)
        self._root.config(menu=menubar)

        menubar.add_command(label="New", command=self.restart)

        fileMenu = Menu(menubar, tearoff=False)
        fileMenu.add_command(label="Modify", command=self._open_modify)
        
        menubar.add_cascade(label="Options", menu=fileMenu)


    def _open_modify(self):
        self._pause_or_resume()
        SettingsW(self._controller.settings, self)


    def restart(self):
        self._pause_or_resume_btn["text"] = "Pause"
        self._text_list.delete(0, END)
        self._controller.restart()
    

    def save_settings(self, settings):
        self._controller.save_settings(settings)
    

    def _write_in_scrollbar(self, text):
        self._text_list.insert(END, text)
        self._text_list.yview(END)


    def _create_buttons(self, root):
        btn_frame = tk.Frame(self._bottom_frame, bg="#263D42")
        btn_frame.pack()
        
        self._pause_or_resume_btn = tk.Button(btn_frame, text="Pause", padx=10,
            pady=5, fg="white", bg="#263D42", command=self._pause_or_resume)
        self._pause_or_resume_btn.grid(row=0, column=0, padx=6)

        next_btn = tk.Button(btn_frame, text="Next", padx=10,
            pady=5, fg="white", bg="#263D42", command=self._next)
        next_btn.grid(row=0, column=1, padx=6)

        stop_btn = tk.Button(btn_frame, text="Stop", padx=10,
            pady=5, fg="white", bg="#263D42", command=self._stop_controller)
        stop_btn.grid(row=0, column=2, padx=6)


    def _pause_or_resume(self):
        self._controller.pause_or_resume()
        if self._pause_or_resume_btn["text"] == "Pause":
            self._pause_or_resume_btn["text"] = "Resume"
        else:
            self._pause_or_resume_btn["text"] = "Pause"


    def _stop_controller(self):
        self._controller.stop()


    def _next(self):
        self._controller.next()
        self._pause_or_resume_btn["text"] = "Pause"


    def _exit_app(self):
        self._controller.stop()
        self._root.quit()
