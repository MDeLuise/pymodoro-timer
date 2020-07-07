from abc import ABC, abstractmethod



class Observer(ABC):
    
    @abstractmethod
    def update(self, state):
        pass



class Observable(ABC):

    def add_observer(self, obs):
        if not '_observers' in vars(self):
            self._observers = []
        
        self._observers.append(obs)


    def remove_observer(self, obs):
        if ('_observers' in vars(self)) and (obs in self._observers):
            self._observers.remove(obs)


    def _notify(self, state):
        for obs in self._observers:
            obs.update(state)