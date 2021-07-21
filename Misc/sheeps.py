from py_stealth.methods import *
from datetime import datetime as dt

SHEEP_CUT = 0x00DF
SHEEP_UNCUT = 0x00CF
CHEST = 0x4C18AFF7
WOOL = 0x0DF8

def get_sheeps(type: int) -> list[int]:
    list = []
    if FindType(type, Ground()):
       list = GetFoundList()
    return list

def train(targets: list[int]) -> None:
    if len(targets) > 0:
        for target in targets:
            if newMoveXY(GetX(target), GetY(target), True, 1, True):
                started = dt.now()
                WaitTargetObject(target)
                UseSkill("Animal Lore")
                WaitJournalLine(started, "not sure|Looks|The animal", 10000)
                Wait(10000)
    else:
        AddToSystemJournal("No targets found")
        Wait(5000)

def cut_sheep(serial: int):
    if IsObjectExists(serial):
        if newMoveXY(GetX(serial), GetY(serial), True, 1, True):
            if IsObjectExists(ObjAtLayer(RhandLayer())):
                started = dt.now()
                if TargetPresent():
                    CancelTarget()
                CancelWaitTarget()
                WaitTargetObject(serial)
                UseObject(ObjAtLayer(RhandLayer()))
                WaitJournalLine(started, "You put", 10000)
                Wait(2000)
            else:
                AddToSystemJournal("No dagger in hand found!")
        else:
            AddToSystemJournal("Unable to get close to sheep!")

def unload_wool():
    if newMoveXY(GetX(CHEST), GetY(CHEST), True, 1, True):
        if FindType(WOOL, Backpack()):
            MoveItem(FindItem(), -1, CHEST, 0, 0, 0)
            Wait(2000)
        AddToSystemJournal("Unloaded")
    else:
        AddToSystemJournal("Failed to reach chest")

if __name__ == "__main__":
    SetARStatus(True)
    SetFindDistance(8)
    while not Dead() and Connected():
        SetWarMode(False)
        for sheep in get_sheeps(SHEEP_UNCUT):
            cut_sheep(sheep)

        unload_wool()
        train(get_sheeps(SHEEP_CUT))

        Wait(5000)
