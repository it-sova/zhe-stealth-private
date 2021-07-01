from py_stealth.methods import *
from datetime import datetime as dt
import inspect

BANK_POINT = (1427, 1694)
CRAFT_POINT = (1388, 1713)
TRASH_POINT = (1426, 1701)
TRASH_ID = 0x48B4B9A5
RESOURCE_TYPE = 0x1BF2
RESOURCE_COLOR = 0x0602
TINKER_TOOLS = 0x1EBC
# Lockpick
# ITEM_TYPE = 0x14FB
# Heating Stand
ITEM_TYPE = 0x1849
STORE_TO_BANK = False
BAD_LOCATIONS = [
    (1415,1704,15),
    (1415,1702,11),
    (1415,1700,7)
]

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

    if level == "ERROR":
        ERRORS =+ 1

    if ERRORS > 10:
        ERRORS = 0
        Disconnect()


def hungry() -> bool:
    if Luck() < 50:
        UOSay(".hungry")
        Wait(1000)
        # if Count(FOOD) > 2:
        #     UseType(FOOD, 0x0000)
        #     Wait(1000)
        #     log(f"Food left in backpack: {Count(FOOD)}", "INFO")
        #     return True
        # else:
        #     log("No more food left in backpack!", "ERROR")
        #     return False

def open_bank() -> None:
    if newMoveXY(bank_x, bank_y, True, 0, True):
        log("Reached bank", "DEBUG")
        log(f"Before backpack usage, LastContainer == {LastContainer()}", "DEBUG")
        while LastContainer() != Backpack():
            UseObject(Backpack())
            Wait(1000)
        log(f"After backpack usage, LastContainer == {LastContainer()}", "DEBUG")
        _try = 0
        while LastContainer() != ObjAtLayer(BankLayer()):
            log(f"Trying to open bank, LastContainer == {LastContainer()}, Bank: {ObjAtLayer(BankLayer())}", "DEBUG")
            _try += 1
            if _try > 10:
                log("Failed to open bank 10 times a row", "CRITICAL")
                exit()
            UOSay("bank")
            Wait(1000)
            if FindTypeEx(ITEM_TYPE, RESOURCE_COLOR, Backpack()):
                if STORE_TO_BANK:
                    MoveItem(FindItem(), -1, ObjAtLayer(BankLayer()), 0, 0, 0)
                    Wait(1000)
        log("Bank opened", "DEBUG")
    else:
        log("Failed to reach bank", "ERROR")

def trash_items():
    if FindTypeEx(ITEM_TYPE, RESOURCE_COLOR, Backpack()):
        log("Trashing items", "DEBUG")
        for _item in GetFoundList():
            MoveItem(_item, -1, TRASH_ID, 0, 0, 0)
            Wait(1000)
        log("Finished trashing", "DEBUG")

def handle_attack(text: str, sender_name: str, sender_id: int):
    if "attacking you" in text:
        log(f"{sender_name} is attacking me", "INFO")
        _data = {"content": f"{CharName()} | {sender_name} is attacking me !"}
        UOSay(".guards")


def grab_from_container(type: int, color: int, qty: int, container: int) -> bool:
    if FindTypeEx(RESOURCE_TYPE, RESOURCE_COLOR, container):
        Grab(FindItem(), 300)
        Wait(1000)
        log("Got ingots from bank", "DEBUG")
        if FindTypeEx(RESOURCE_TYPE, RESOURCE_COLOR, container):
            log(f"Resource left in container: {FindFullQuantity()}", "INFO")
        craft_tools()
        return True
    log("Failed to get ingots from bank", "ERROR")
    return False


def craft_item(category: str, item: str) -> None:
    log(f"Crafting {item}", "DEBUG")
    if FindTypeEx(RESOURCE_TYPE, RESOURCE_COLOR, Backpack()):
        _started = dt.now()
        CancelAllMenuHooks()
        cancel_targets()
        WaitMenu("What would you like to make?", category)
        WaitMenu("What would you like to make?", item)
        WaitTargetObject(FindItem())
        UseType(TINKER_TOOLS, -1)
        WaitJournalLine(_started, "finished|aborted", 10000)
    Wait(500)

def craft_tools() -> None:
    pass
    if Count(TINKER_TOOLS) < 5:
        log("Not enought tools in pack, let's craft some", "DEBUG")
        while Count(TINKER_TOOLS) < 5:
            craft_item("Tools", "Tinker")
            Wait(1000)

if __name__ == "__main__":
    bank_x, bank_y = BANK_POINT
    craft_x, craft_y = CRAFT_POINT
    # Fuck the portals
    for bad_location in BAD_LOCATIONS:
        bad_x, bad_y, _ = bad_location
        SetBadLocation(bad_x, bad_y)
    # Fuck the portals 2nd time
    SetBadObject(0x0F6C, 0xFFFF, 3)
    SetEventProc("evSpeech", handle_attack)
    SetARStatus(True)
    ClearSystemJournal()
    SetPauseScriptOnDisconnectStatus(True)
    CancelAllMenuHooks()
    cancel_targets()
    UOSay(".autoloop 1")
    if newMoveXY(craft_x, craft_y, True, 0, True):
        log("Reached crafting point", "DEBUG")
    while not Dead() and Connected():
        if FindTypeEx(RESOURCE_TYPE, RESOURCE_COLOR, Backpack()) and FindQuantity() > 20:
            log("Crafting started", "DEBUG")
            craft_item("Tools", "Heating")
            log("Crafting finished", "DEBUG")
            if FindTypeEx(RESOURCE_TYPE, RESOURCE_COLOR, Backpack()):
                log(f"Resource left in pack: {FindFullQuantity()}", "INFO")
            hungry()
        else:
            if not STORE_TO_BANK:
                log("Will trash items", "DEBUG")
                if newMoveXY(TRASH_POINT[0], TRASH_POINT[1], True, 0, False):
                    log("Reached trash point", "DEBUG")
                    trash_items()
                    Wait(1000)
            open_bank()
            grab_from_container(RESOURCE_TYPE, RESOURCE_COLOR, 500, ObjAtLayer(BankLayer()))
            if newMoveXY(craft_x, craft_y, True, 0, True):
                log("Reached crafting point", "DEBUG")

