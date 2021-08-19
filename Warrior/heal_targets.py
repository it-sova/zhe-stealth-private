from py_stealth.methods import *
from datetime import datetime as dt

BANDAGES = 0x0E21
#TARGETS = [0x00287C80, 0x00285CEB]
TARGETS = [0x00288E25]
FOOD = 0x097B

def hungry(container: int) -> bool:
    if Luck() < 90:
        if FindType(FOOD, container):
            if FindFullQuantity() > 20:
                UseObject(FindItem())
                Wait(1000)
                UseObject(Self())
                Wait(1000)
            else:
                AddToSystemJournal("No more food left in backpack!")
                return False
    return True

def heal(target: int):
    _start = dt.now()
    if FindType(BANDAGES, -1):
        WaitTargetObject(target)
        UseObject(FindItem())
        WaitJournalLine(_start, "Bloody Bandages|This patient|You healed", 30000)
    else:
        AddToSystemJournal("No bandages found")


if __name__ == "__main__":
    while not Dead() and Connected():
        hungry(-1)
        for target in TARGETS:
            if IsObjectExists(target):
                if GetHP(target) < GetMaxHP(target):
                    AddToSystemJournal(f"Healing {GetName(target)}")
                    newMoveXY(GetX(target), GetY(target), True, 1, True)
                    heal(target)
                    Wait(1000)
        Wait(1000)



