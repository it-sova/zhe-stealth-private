from py_stealth.methods import *
from datetime import datetime as dt

BANDAGES = 0x0E21
TARGETS = [0x0027E98E, 0x00247664]

def heal(target: int):
    _start = dt.now()
    if FindType(BANDAGES, -1):
        WaitTargetObject(target)
        UseObject(FindItem())
        WaitJournalLine(_start, "Bloody Bandages|cure|poison", 10000)
    else:
        AddToSystemJournal("No bandages found")


if __name__ == "__main__":
    while not Dead() and Connected():
        for target in TARGETS:
            if IsObjectExists(target):
                if GetHP(target) < GetMaxHP(target):
                    AddToSystemJournal(f"Healing {GetName(target)}")
                    newMoveXY(GetX(target), GetY(target), True, 1, True)
                    heal(target)
                    Wait(1000)
        Wait(1000)



