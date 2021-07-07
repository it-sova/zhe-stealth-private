from py_stealth.methods import *
from datetime import datetime as dt

LOGS = 0x1BDD


def grab_from_container(type: int, color: int, qty: int, container: int) -> bool:
    if FindTypeEx(type, color, container) and FindQuantity() >= qty:
        Grab(FindItem(), qty)
        Wait(1000)
        return True
    return False


if __name__ == "__main__":
    AutoMenu("What would", "Stuff")
    AutoMenu("What would", "Shaft")
    while not Dead():
        if not FindType(LOGS, Backpack()):
            while not grab_from_container(LOGS, 0x0000, 1, 0x4C1116AF):
                Wait(2000)
                AddToSystemJournal("No logs left in container")
        else:
            _started = dt.now()
            UseObject(ObjAtLayer(RhandLayer()))
            WaitTargetObject(FindItem())

            WaitJournalLine(_started, "You stop", 60000)
            Wait(1000)
        Wait(500)