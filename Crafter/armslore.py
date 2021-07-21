from py_stealth.methods import *
from datetime import datetime as dt

TARGET = 0x0F51
FOOD = 0x097B


def hungry() -> bool:
    if Luck() < 90:
        if Count(FOOD) > 2:
            UseType(FOOD, 0x0000)
            Wait(1000)
        else:
            return False
    return True


def cancel_targets() -> None:
    if TargetPresent():
        CancelTarget()
    CancelWaitTarget()

if __name__ == "__main__":
    while not Dead() and Connected():
        if FindType(TARGET, Backpack()):
            for item in GetFoundList():
                hungry()
                cancel_targets()
                WaitTargetObject(item)
                UseSkill("Arms Lore")
                started = dt.now()
                WaitJournalLine(started, "Status", 10 * 1000)
                Wait(10 * 1000)

