from Scripts.Crafter.mining import grab_from_container
from py_stealth.methods import *
from datetime import datetime as dt
import inspect

SAW_TYPE = 0x1035
TOOL_CHEST = 0x4C18AFE8
LOGS = 0x1BDD
TRASH = 0x4C1A6AB0
COLOR = 0x0000
FOOD = 0x097B


def get_target_item_and_category(classed: bool = True) -> list[str, str, str, int]:
    classed_bonus = 5 if classed else 0
    # Classed crafters have -5 skill requirement to craft item
    # So take default value from table and reduce it if character is classed
    # If it's not a crafter - bad for you
    skill_value = GetSkillValue("Carpentry")
    if skill_value <= 40 - classed_bonus:
        return ["Shield", "Torch", [0x0F64]]
    if skill_value <= 52 - classed_bonus:
        return ["Shield", "Club", [0x13B3]]
    if skill_value <= 65 - classed_bonus:
        return ["Shield", "Wooden Shield", [0x1B7A]]
    elif skill_value <= 73 - classed_bonus:
        return ["Chairs", "Fancy", [0x14F0]]
    elif skill_value <= 80 - classed_bonus:
        return ["Staffs", "Quarter", [0x0E8A,0x2396]]
    elif skill_value <= 100 - classed_bonus:
        return ["Staffs", "Black", [0x0DF0,0x2390]]
    else:
        return ["Staffs", "Black", [0x0DF0,0x2390]]

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

def get_item_from_container(type: int, color: int, container: int, name: str = "") -> bool:
    open_container()
    if FindTypeEx(type, color, container, False):
        Grab(FindItem(), 1)
        Wait(500)
        if len(name) > 0:
            log(f"{name} left in container: {FindCount()}")
        return FindTypeEx(type, color, Backpack(), False)

def enough_resources():
    if FindTypeEx(LOGS, COLOR, Ground(), False):
        log(f"There is {FindFullQuantity()} logs left", "INFO")
    return True if FindFullQuantity() > 100 else False

def craft_item(item_details: list[str]):
    item_name = item_details[-2]
    log(f"Crafting {item_name}", "DEBUG")
    if FindTypeEx(LOGS, COLOR, Ground(), False):
        _started = dt.now()
        CancelAllMenuHooks()
        cancel_targets()
        WaitTargetObject(FindItem())
        UseType(SAW_TYPE, 0xFFFF)
        Wait(500)
        for category in item_details[:2]:
            #log(f"Selecting {category}")
            WaitMenu("What", category)
        WaitJournalLine(_started, "finished|aborted", 600000)
    Wait(500)

def full_disconnect():
    SetARStatus(False)
    Disconnect()
    exit()


def is_classed() -> bool:
    _started = dt.now()
    UOSay(".skill")
    Wait(5000)
    NumGumpButton(0, 0)
    if InJournalBetweenTimes("not classed", _started, dt.now()) > 0:
        log("Character not classed","INFO")
        return False
    log("Character classed","INFO")
    return True


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
    classed = is_classed()
    while not Dead() and Connected():
        item_to_craft = get_target_item_and_category(classed)
        resulting_item = item_to_craft[-1]
        if not hungry() or not enough_resources():
            log("No food or resources!", "CRITICAL")
            #full_disconnect()

        if not FindType(SAW_TYPE, Backpack()):
            grab_from_container(SAW_TYPE, -1, 1, TOOL_CHEST)

        craft_item(item_to_craft)
        #if FindType(resulting_item, Backpack()):
        if FindTypesArrayEx(resulting_item, [COLOR], [Backpack()], [False]):
            for item in GetFoundList():
                MoveItem(item, 1, TRASH, 0, 0, 0)
                Wait(1000)
        Wait(100)



