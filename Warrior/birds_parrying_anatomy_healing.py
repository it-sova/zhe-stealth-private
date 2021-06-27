#from py_stealth.methods import AddToSystemJournal, BandageSelf, CancelTarget, CancelWaitTarget, Count, Equip, FindItem, FindType, FindTypeEx, GetFoundList, GetHP, IsObjectExists, LhandLayer, ObjAtLayer, SetFindDistance, SetWarMode, TargetPresent, UOSay, UseSkill, Wait, WaitForTarget, WaitJournalLine, WaitTargetObject, WarMode
from py_stealth.methods import *
from datetime import datetime as dt

FISH = 0x097B
SHIELD = 0x1B76
ANIMALS = [0x0005,0x0006]
BANDAGES = 0x0E21

def equip_shield():
    if not ObjAtLayer(LhandLayer()):
        print("Rearm shield")
        if FindType(SHIELD):
            Equip(LhandLayer(), FindItem())
            Wait(1000)
        else:
            print("No more shields left!")

def disable_warmode():
    if WarMode():
        SetWarMode(False)

def heal():
    #TODO: Percent
    _treshold = 90
    if HP() < _treshold and Count(BANDAGES) > 2:
        _start = dt.now()
        UOSay(".bandageself")
        WaitJournalLine(_start, "Bloody Bandages|cure|poison", 10000)


def get_animals():
    _result = []
    for _animal in ANIMALS:
        SetFindDistance(1)
        if FindType(_animal, Ground()):
            _result += GetFoundList()
    return _result

def anatomy(animals = []):
    for _animal in animals:
        if IsObjectExists(_animal):
            heal()
            equip_shield()
            disable_warmode()
            if TargetPresent():
                CancelTarget()
            CancelWaitTarget()
            WaitTargetObject(_animal)
            UseSkill("Anatomy")
            WaitForTarget(1000)
            _started = dt.now()
            WaitJournalLine(_started, "not sure|somewhat|Stamina", 1000)
            Wait(13 * 1000)

def hungry():
    if Luck() < 90 and Count(FISH) > 2:
        UseType(FISH, 0x0000)
        Wait(1000)


if __name__ == "__main__":
    while not Dead():
        animals = get_animals()
        anatomy(animals)
        hungry()
