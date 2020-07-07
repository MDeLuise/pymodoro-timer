from abc import ABC, abstractmethod
from datetime import datetime, timedelta



class State(ABC):
    def __init__(self, settings, label, inc_pom_after=False):
        self._settings = settings
        self.time = self._return_time()
        self.inc_after = inc_pom_after
        self.time_label = label

    @abstractmethod
    def _return_time(self):
        pass

    @abstractmethod
    def next(self, actual_pom):
        pass

    def recompute_time(self, time_remaining):
        self.time = time_remaining

    def _from_now_to(self):
        actual_datetime = datetime.now()
        time_delta = timedelta(seconds=self.time)
        return (actual_datetime + time_delta).strftime("%H:%M:%S")



class Idle(State):
    def __init__(self, settings):
        super().__init__(settings, "Idle")

    def _return_time(self):
        return -1

    def next(self, actual_pom):
        return Work(self._settings)


class Pause(State):
    def __init__(self, settings, prev_state):
        super().__init__(settings, "Paused at:")
        self._paused_from = prev_state

    def _return_time(self):
        return -1

    def next(self, actual_pom):
        return self._paused_from

    def __repr__(self):
        return "Pomodoro paused"


class Work(State):
    def __init__(self, settings):
        super().__init__(settings, "Work for:", inc_pom_after=True)

    def _return_time(self):
        return self._settings["work"]

    def next(self, starting_pom):
        next_state = (Long if starting_pom == 0 else Short)
        return next_state(self._settings)

    def __repr__(self):
        return f"Work until {self._from_now_to()}"


class Short(State):
    def __init__(self, settings):
        super().__init__(settings, "Relax for:")

    def _return_time(self):
        return self._settings["short"]

    def next(self, actual_pom):
        return Work(self._settings)

    def __repr__(self):
        return f"Hey! Take a short break until {self._from_now_to()}"


class Long(State):
    def __init__(self, settings):
        super().__init__(settings, "Relax for:")

    def _return_time(self):
        return self._settings["long"]

    def next(self, actual_pom):
        return Work(self._settings)

    def __repr__(self):
        return f"Hey! Take a long break until {self._from_now_to()}"