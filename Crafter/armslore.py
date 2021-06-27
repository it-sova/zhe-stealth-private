from py_stealth.methods import *
from datetime import datetime as dt

TARGET = 0x0E85

def cancel_targets() -> None:
    if TargetPresent():
        CancelTarget()
    CancelWaitTarget()

if __name__ == "__main__":
    while not Dead() and Connected():
        if FindType(TARGET, Backpack()):
            for item in GetFoundList():
                cancel_targets()
                WaitTargetObject(item)
                UseSkill("Arms Lore")
                started = dt.now()
                WaitJournalLine(started, "Status", 10 * 1000)
                Wait(10 * 1000)

