import os, sys
import json

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from model.observer import Observer
from model import state
from model.timer import Timer



class Controller(Observer):

    def __init__(self, settings_file, ui):
        self._pom_done = 0 # pomodoro ALREADY fully completed
        self._setting_file = settings_file
        self._load_settings()
        self._state = state.Idle(self._settings)
        self._ui = ui
        ui.link_controller(self)


    def _load_settings(self):
        with open(self._setting_file) as fp:
            self._settings = json.load(fp)


    def save_settings(self, settings):
        with open(self._setting_file, 'w') as fp:
            json.dump(settings, fp)


    def update(self, state):
        # <= and not only == because (in case of delay in timer or in this class) can arrive a
        # timer like {min: 0, sec: -1} for example and not seeing the {min: 0, sec: 0} moment
        if state["min"] <= 0 and state["sec"] <= 0:
            self.start()
        else:
            self._ui.update_time(state)


    def next(self):
        if '_timer' in vars(self):
            self._timer.remove_observer(self)

        # because next of "Pause" is the previous state, so twice "next()"
        # needed (the other in "start()")
        if type(self._state) == state.Pause:
            self._state = self._state.next(self._current_pom())
        
        self.start()


    def pause_or_resume(self):
        if type(self._state) != state.Pause:
            self._pause()
        else:
            self._resume()


    def restart(self):
        if '_timer' in vars(self):
            self._timer.remove_observer(self)
        self.__init__(self._setting_file, self._ui)
        self.start()


    def _resume(self):
        self._state = self._state.next(self._current_pom())
        self._state.recompute_time(self._timer.after_pause())
        self._ui.print({
            "state": self._state,
            "pom": self._current_pom(),
            "pom_set": self._settings["pom"]})
        self._timer.start()


    def stop(self):
        os._exit(0)


    def start(self):
        self._change_state()
        self._start_and_register_timer()


    def _pause(self):
        self._timer.pause()
        self._state = state.Pause(self._settings, self._state)
        self._ui.print({
            "state": self._state,
            "pom": self._current_pom(),
            "pom_set": self._settings["pom"]})


    def _start_and_register_timer(self):
        self._timer = Timer(self._state.time)
        self._timer.add_observer(self)
        self._timer.start()


    def _current_pom(self):
        return (self._pom_done % self._settings["pom"])


    def _change_state(self):
        if self._state.inc_after:
            self._pom_done += 1

        self._state = self._state.next(self._current_pom())
        self._ui.print({
            "state": self._state,
            "pom": self._current_pom(),
            "pom_set": self._settings["pom"]})


    @property
    def settings(self):
        return self._settings
