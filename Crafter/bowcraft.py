from py_stealth.methods import *
from datetime import datetime as dt
import inspect

DAGGER = 0x0F51
TOOL_CHEST = 0x4C18AFE8
LOGS = 0x1BDD
TRASH = 0x4C1A6AB0
FOOD = 0x097B


def get_target_item_and_category(classed: bool = True) -> list[str, str, str, int]:
    classed_bonus = 5 if classed else 0
    # Classed crafters have -5 skill requirement to craft item
    # So take default value from table and reduce it if character is classed
    # If it's not a crafter - bad for you
    skill_value = GetSkillValue("Bowcraft")
    if skill_value <= 40 - classed_bonus:
        return {"menu_items": ["Stuff", "Kindling"],
                "resulting_items_types": [0x0DE1],
                "resource_type": LOGS,
                "resource_color": 0x0000,
                "resource_qty": 1,
                "resource_name": "logs",
                "keep_resulting_item": True}
    elif skill_value <= 75 - classed_bonus:
        return {"menu_items": ["Stuff", "Shaft"],
                "resulting_items_types": [0x1BD4],
                "resource_type": LOGS,
                "resource_color": 0x0000,
                "resource_qty": 1,
                "resource_name": "logs",
                "keep_resulting_item": True}
    elif skill_value <= 85 - classed_bonus:
        return {"menu_items": ["Weapons", "Bow"],
                "resulting_items_types": [0x13B2],
                "resource_type": LOGS,
                "resource_color": 0x0000,
                "resource_qty": 80,
                "resource_name": "logs",
                "keep_resulting_item": False}
    elif skill_value <= 90 - classed_bonus:
        return {"menu_items": ["Weapons", "Crossbow"],
                "resulting_items_types": [0x0F4F],
                "resource_type": LOGS,
                "resource_color": 0x0000,
                "resource_qty": 120,
                "resource_name": "logs",
                "keep_resulting_item": False}
    elif skill_value <= 150 - classed_bonus:
        return {"menu_items": ["Weapons", "Heavy Crossbow"],
                "resulting_items_types": [0x13FD],
                "resource_type": LOGS,
                "resource_color": 0x0362,
                "resource_qty": 160,
                "resource_name": "logs",
                "keep_resulting_item": False}
    else:
        return {"menu_items": ["Weapons", "Heavy Crossbow"],
                "resulting_items_types": [0x13FD],
                "resource_type": LOGS,
                "resource_color": 0x0362,
                "resource_qty": 160,
                "resource_name": "logs",
                "keep_resulting_item": False}

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
            Wait(2000)

        _try = 0
        while LastContainer() != TOOL_CHEST:
            UseObject(TOOL_CHEST)
            Wait(2000)
            _try += 1
            if _try >= 10:
                log("Failed to open tool chest 10 times a row", "CRITICAL")
                full_disconnect()
    else:
        log("Tool chest not found!", "CRITICAL")

def get_item_from_container(type: int, color: int, container: int, name: str = "", qty: int = 1) -> bool:
    if container != 0:
        open_container()

    if FindTypeEx(type, color, container, False):
        Grab(FindItem(), qty)
        Wait(2000)
        if len(name) > 0:
            log(f"{name} left in container: {FindCount()}")
        return FindTypeEx(type, color, Backpack(), False)

def enough_resources(resource: int, color:int, name: str = ""):
    if FindTypeEx(resource, color, Ground(), False):
        log(f"There is {FindFullQuantity()} {name} left", "INFO")
    return True if FindFullQuantity() > 100 else False

def craft_item(item_details: dict):
    log(f"Crafting {item_details['menu_items'][-1]}", "DEBUG")
    if FindTypeEx(item_details["resource_type"], item_details["resource_color"], Backpack(), False):
        _started = dt.now()
        CancelAllMenuHooks()
        cancel_targets()
        WaitTargetObject(FindItem())
        UseType(DAGGER, 0xFFFF)
        Wait(500)
        for category in item_details['menu_items']:
            WaitMenu("What", category)
        WaitJournalLine(_started, "You stop to", 600000)
    Wait(1000)

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
    Wait(2000)
    while not Dead() and Connected():
        crafting_details = get_target_item_and_category(classed)

        if not hungry() or not enough_resources(
                                    crafting_details["resource_type"],
                                    crafting_details["resource_color"],
                                    crafting_details["resource_name"]):
            log("No food or resources!", "CRITICAL")
            #full_disconnect()

        if not FindType(DAGGER, Backpack()):
            get_item_from_container(DAGGER, 0xFFFF, TOOL_CHEST, "Dagger")

        if not FindType(crafting_details["resource_type"], Backpack()) or FindQuantity() < crafting_details["resource_qty"]:
            get_item_from_container(crafting_details["resource_type"], crafting_details["resource_color"], Ground(), crafting_details["resource_name"], crafting_details["resource_qty"])

        craft_item(crafting_details)
        destination_container = TOOL_CHEST if crafting_details["keep_resulting_item"] else TRASH

        if FindTypesArrayEx(crafting_details["resulting_items_types"], [crafting_details["resource_color"]], [Backpack()], [False]):
            for item in GetFoundList():
                MoveItem(item, -1, destination_container, 0, 0, 0)
                Wait(1000)
        Wait(100)



