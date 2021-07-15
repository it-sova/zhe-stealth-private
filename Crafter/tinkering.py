from Scripts.Crafter.mining import grab_from_container
from py_stealth.methods import *
from datetime import datetime as dt
import inspect

TINKER_TOOLS = 0x1EBC
TOOL_CHEST = 0x4C18AFE8
LOGS = 0x1BDD
INGOTS = 0x1BF2
TRASH = 0x4C1A6AB0
FOOD = 0x097B


def get_target_item_and_category(classed: bool = True) -> list[str, str, str, int]:
    classed_bonus = 5 if classed else 0
    # Classed crafters have -5 skill requirement to craft item
    # So take default value from table and reduce it if character is classed
    # If it's not a crafter - bad for you
    skill_value = GetSkillValue("Carpentry")
    if skill_value <= 41 - classed_bonus:
        return {"menu_items": ["Tools", "Froe"],
                "resulting_items_types": [0x10E5],
                "resource_type": INGOTS,
                "resource_color": 0x0602,
                "resource_name": "ingots"}
    elif skill_value <= 60 - classed_bonus:
        return {"menu_items": ["Tools", "lockpick"],
                "resulting_items_types": [0x14FB],
                "resource_type": INGOTS,
                "resource_color": 0x0602,
                "resource_name": "ingots"}
    elif skill_value <= 64 - classed_bonus:
        return {"menu_items": ["Kitchenware", "Frying"],
                "resulting_items_types": [0x097F],
                "resource_type": INGOTS,
                "resource_color": 0x0602,
                "resource_name": "ingots"}
    elif skill_value <= 80 - classed_bonus:
        return {"menu_items": ["Tools", "Heating"],
                "resulting_items_types": [0x1849],
                "resource_type": INGOTS,
                "resource_color": 0x0602,
                "resource_name": "ingots"}
    else:
        return {"menu_items": ["Tools", "Heating"],
                "resulting_items_types": [0x1849],
                "resource_type": INGOTS,
                "resource_color": 0x0602,
                "resource_name": "ingots"}

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

def enough_resources(resource: int, color:int, name: str = ""):
    if FindTypeEx(resource, color, Ground(), False):
        log(f"There is {FindFullQuantity()} {name} left", "INFO")
    return True if FindFullQuantity() > 100 else False

def craft_item(item_details: dict):
    log(f"Crafting {item_details['menu_items'][-1]}", "DEBUG")
    if FindTypeEx(item_details["resource_type"], item_details["resource_color"], Ground(), False):
        _started = dt.now()
        CancelAllMenuHooks()
        cancel_targets()
        WaitTargetObject(FindItem())
        UseType(TINKER_TOOLS, 0xFFFF)
        Wait(500)
        for category in item_details['menu_items']:
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
        crafting_details = get_target_item_and_category(classed)

        if not hungry() or not enough_resources(
                                    crafting_details["resource_type"],
                                    crafting_details["resource_color"],
                                    crafting_details["resource_name"]):
            log("No food or resources!", "CRITICAL")
            #full_disconnect()

        if not FindType(TINKER_TOOLS, Backpack()):
            grab_from_container(TINKER_TOOLS, -1, 1, TOOL_CHEST)

        craft_item(crafting_details)
        #if FindType(resulting_item, Backpack()):
        if FindTypesArrayEx(crafting_details["resulting_items_types"], [crafting_details["resource_color"]], [Backpack()], [False]):
            for item in GetFoundList():
                MoveItem(item, -1, TRASH, 0, 0, 0)
                Wait(1000)
        Wait(100)



