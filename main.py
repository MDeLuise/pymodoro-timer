import sys
import threading

from controller.controller import Controller
from view.views import CLI, GUI
import os


SETTINGS_FILE = os.path.dirname(sys.argv[0]) + ".settings.json"



if (__name__ == "__main__"):

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Possible option:",
            "--cli (for command line interface version of the app)",
            "--no-notify (for no time notify)", sep='\n')
        sys.exit(0)
    elif "--cli" in sys.argv:
        ui = CLI(not "--no-notify" in sys.argv)
    else:
        ui = GUI(not "--no-notify" in sys.argv)
    
    controller = Controller(SETTINGS_FILE, ui)
    try:
        controller.start()
        while True:
            pass
    except KeyboardInterrupt:
        print("")
        controller.stop()
        sys.exit(0)