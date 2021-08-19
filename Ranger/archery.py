from py_stealth.methods import *
from datetime import datetime as dt


FOOD = 0x097B
EQUIP_CHEST = 0x4C2062F2
BOW = 0x13B2
ARROWS = 0x0F3F
TARGET = 0x00288E25

def hungry(container: int) -> bool:
    if Luck() < 90:
        if FindType(FOOD, container):
            if FindFullQuantity() > 20:
                UseObject(FindItem())
                Wait(1000)
                AddToSystemJournal(f"Food left in container: {FindFullQuantity()}")
            else:
                AddToSystemJournal("No more food left in backpack!")
                return False
    return True

def full_disconnect():
    SetARStatus(False)
    Disconnect()
    exit()

def open_container(container: int):
    if IsObjectExists(container):
        while LastContainer() != Backpack():
            UseObject(Backpack())
            Wait(2000)

        _try = 0
        while LastContainer() != container:
            UseObject(container)
            Wait(1000)
            _try += 1
            if _try >= 10:
                AddToSystemJournal("Failed to open tool checst 10 times a row")
                full_disconnect()
    else:
        AddToSystemJournal("Container not found!")

def get_item_from_container(type: int, color: int, container: int, name: str = "") -> bool:
    open_container(container)
    if FindTypeEx(type, color, container, False):
        Grab(FindItem(), 1)
        Wait(1000)
        if len(name) > 0:
            AddToSystemJournal(f"{name} left in container: {FindCount()}")
        return FindTypeEx(type, color, Backpack(), False)

def equip_item_on_layer(type: int, layer: int, name: str = ""):
    if not ObjAtLayer(layer):
        if FindType(type):
            Equip(layer, FindItem())
            Wait(2000)
        else:
            if get_item_from_container(type, -1, EQUIP_CHEST, name):
                AddToSystemJournal(f"Rearm {name}")
                equip_item_on_layer(type, layer)
            else:
                AddToSystemJournal("Unable to get shield from container!")


def check_enemy_hp(enemy: int):
    if IsObjectExists(enemy):
        while GetHP(enemy) < 300:
            SetWarMode(False)
            Wait(100)

if __name__ == "__main__":
    UnEquip(LhandLayer())
    UnEquip(RhandLayer())
    SetFindDistance(3)
    SetARStatus(True)
    ClearSystemJournal()
    loop = 0
    while not Dead() and Connected():
        check_enemy_hp(TARGET)
        equip_item_on_layer(BOW, RhandLayer(), "Bow")
        if not FindType(ARROWS, Backpack()) or FindFullQuantity() < 20:
            if FindType(ARROWS, Ground()):
                AddToSystemJournal(f"Arrows left: {FindFullQuantity()}")
                Grab(FindItem(), 100)
                Wait(1000)
            else:
                AddToSystemJournal("No more arrows left")
                full_disconnect()

        if IsObjectExists(TARGET):
            Attack(TARGET)

        loop += 1
        if loop > 20:
            hungry(-1)
            loop = 0
        Wait(1000)




