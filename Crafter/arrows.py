from py_stealth.methods import *
from datetime import datetime as dt
import inspect

DAGGER = 0x0F51
TOOL_CHEST = 0x4C18AFE8
FEATHERS = 0x1BD1
SHAFTS = 0x1BD4
ARROWS = 0x0F3F
FOOD = 0x097B

def cancel_targets() -> None:
    if TargetPresent():
        CancelTarget()
    CancelWaitTarget()

def log(message: str, level: str = "DEBUG") -> None:
    _verbosity_level = {
        "DEBUG":    1,
        "INFO":     2,
        "ERROR":    3,
        "CRITICAL": 4
    }

    if _verbosity_level[level] >= 1:
        AddToSystemJournal(f"[{level}] ({inspect.stack()[1].function}) {message}")


def hungry() -> bool:
    if Luck() < 90:
        if Count(FOOD) > 2:
            UseType(FOOD, 0x0000)
            Wait(1000)
            log(f"Food left in backpack: {Count(FOOD)}", "INFO")
        else:
            log("No more food left in backpack!", "ERROR")
            return False
    return True

def open_container():
    if IsObjectExists(TOOL_CHEST):
        while LastContainer() != Backpack():
            UseObject(Backpack())
            Wait(1000)

        _try = 0
        while LastContainer() != TOOL_CHEST:
            UseObject(TOOL_CHEST)
            Wait(100)
            _try += 1
            if _try >= 10:
                log("Failed to open tool chest 10 times a row", "CRITICAL")
                full_disconnect()
    else:
        log("Tool chest not found!", "CRITICAL")
        full_disconnect()

def get_item_from_container(type: int, color: int, container: int, name: str = "") -> bool:
    if container != 0:
        open_container()

    if FindTypeEx(type, color, container, False):
        Grab(FindItem(), 200)
        Wait(500)
        if len(name) > 0:
            log(f"{name} left in container: {FindQuantity()}")
        return FindTypeEx(type, color, Backpack(), False)

def enough_resources(resource: int, color:int, name: str = ""):
    FindTypeEx(resource, color, Ground(), False)
    return True if FindFullQuantity() > 100 else False

def craft_item():
    log(f"Crafting 30 arrows", "DEBUG")
    if FindTypeEx(FEATHERS, 0xFFFF, Backpack(), False):
        _started = dt.now()
        CancelAllMenuHooks()
        cancel_targets()
        WaitTargetObject(FindItem())
        UseType(SHAFTS, 0xFFFF)
        Wait(500)
        WaitMenu("What", "Arrow")
        WaitMenu("How many", "30 arrows")
        WaitJournalLine(_started, "You stop to", 600000)
    Wait(1000)

def full_disconnect():
    SetARStatus(False)
    Disconnect()
    exit()

def init() -> None:
    SetARStatus(True)
    SetPauseScriptOnDisconnectStatus(True)
    ClearSystemJournal()
    UOSay(".checkDeed 1")
    Wait(100)
    UOSay(".checkExcept 1")
    Wait(100)
    UOSay(".checkPerfect 1")
    Wait(100)
    UOSay(".autoloop 10")
    Wait(100)

if __name__ == "__main__":
    init()
    while not Dead() and Connected():
        for resource in [FEATHERS, SHAFTS]:
            if not enough_resources(resource, 0x0000):
                log("Not enogh resources!")
                full_disconnect()

        hungry()
        if not FindType(FEATHERS, Backpack()) or FindQuantity() < 100:
            get_item_from_container(FEATHERS, 0x0000, Ground(), "Feathers")

        if not FindType(SHAFTS, Backpack()) or FindQuantity() < 100:
            get_item_from_container(SHAFTS, 0x0000, Ground(), "Shafts")

        craft_item()

        if FindType(ARROWS, Backpack()):
            arrows = FindItem()
            if FindType(ARROWS, Ground()):
                log(f"Arrows: {FindFullQuantity()}")
                MoveItem(arrows, -1, FindItem(), 0, 0, 0)
                Wait(2000)
            else:
                DropHere(arrows)
        Wait(100)



