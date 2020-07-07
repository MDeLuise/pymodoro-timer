# below whould be correct, if module "observer"
# whould not be imported even in controller.py
#from observer import Observable

from model.observer import Observable
import threading
import time
import math



class Timer(Observable):

    def __init__(self, seconds):
        self._countdown = seconds
        self._num_timers = 0


    def start(self):
        if (not '_timer' in vars(self)) or (not self._timer.isAlive()):
            self._started_timer = int(time.time())
            self._timer = threading.Thread(target=self._notify_loop)
            self._timer.start()


    def pause(self):
        if (not self._started_timer is None):
            self._countdown -= int(int(time.time()) - self._started_timer) 
            self._num_timers += 1 # so running thread does not notify


    def _notify_loop(self):
        my_id = self._num_timers
        self._num_timers += 1
        remaining = 42 # any number > 0 whould be good
        
        while(self._num_timers == (my_id + 1) and remaining > 0):
            remaining = self._countdown - (int(time.time() - self._started_timer))
            self._notify(self._from_sec_to_dict(remaining))
            time.sleep(1)


    def after_pause(self):
        return self._countdown


    def _from_sec_to_dict(self, tot_sec):
        if tot_sec <= 60:
            return {"min": 0, "sec": tot_sec}
        minu = math.floor(tot_sec / 60)
        seco = tot_sec - (minu * 60)
        return {"min": minu, "sec": seco}