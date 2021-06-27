from py_stealth.methods import *
from datetime import datetime as dt

FISH = 0x097B
FOOD_TYPE = 0x1608

def hungry():
    if Luck() < 90 and Count(FISH) > 2:
        UseType(FISH, 0x0000)
        Wait(1000)


if __name__ == "__main__":
    SetARStatus(True)
    SetPauseScriptOnDisconnectStatus(True)
    while not Dead():
        if FindType(FOOD_TYPE, Backpack()):
            for _food in GetFoundList():
                hungry()
                if TargetPresent():
                    CancelTarget()
                CancelWaitTarget()

                WaitTargetObject(_food)
                UseSkill("Taste Identification")

                _started = dt.now()
                WaitJournalLine(_started, "contains|not sure", 5000)
                Wait(10 * 1000)
        Wait(100)
