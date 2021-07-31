from py_stealth.methods import *
from datetime import datetime as dt

FOOD = 0x097B

def hungry() -> bool:
    if Luck() < 90:
        if Count(FOOD) > 2:
            UseType(FOOD, 0x0000)
            Wait(1000)
        else:
            return False
    return True


if __name__ == "__main__":
    AutoMenu("Select", "(last)")
    while not Dead() and Connected():
        started = dt.now()
        hungry()
        UseSkill("Tracking")
        Wait(10000)
