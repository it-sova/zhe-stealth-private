from py_stealth.methods import *
from datetime import datetime as dt


TARGETS = [0x00CF, 0x00DF, 0x00D3, 0x00DC, 0x0005]
FOOD = 0x097B

def find_targets(types: list[int]) -> list[int]:
    targets = []
    if FindTypesArrayEx(TARGETS, [0xFFFF], [Ground()], [False]):
        AddToSystemJournal(f"Targets found: {len(GetFoundList())}")
        return GetFoundList()

    return targets

def train(targets: list[int]) -> None:
    if len(targets) > 0:
        for target in targets:
            #if newMoveXY(GetX(target), GetY(target), True, 1, True):
            started = dt.now()
            WaitTargetObject(target)
            UseSkill("Anatomy")
            WaitJournalLine(started, "Stamina", 10000)
            Wait(10000)
    else:
        AddToSystemJournal("No targets found")
        Wait(5000)

def hungry() -> bool:
    if Luck() < 90:
        if Count(FOOD) > 2:
            UseType(FOOD, 0x0000)
            Wait(1000)
            AddToSystemJournal(f"Food left in backpack: {Count(FOOD)}")
        else:
            AddToSystemJournal("No more food left in backpack!")
            return False
    return True

if __name__ == "__main__":
    SetFindDistance(10)
    while not Dead() and Connected():
        hungry()
        train(find_targets(TARGETS))
        Wait(2000)
