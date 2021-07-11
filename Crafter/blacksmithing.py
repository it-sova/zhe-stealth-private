from Scripts.Crafter.mining import INGOTS
from py_stealth.methods import *
from datetime import datetime as dt
import inspect

HAMMER_TYPE = 0x13E3
TONGS_TYPE = 0x0FBB
TOOL_CHEST = 0x4C18AFE8
INGOTS = 0x1BF2
COLOR = 0x0602
FOOD = 0x097B


def get_target_item_and_category() -> list[str, str, str, int]:
    skill_value = GetSkillValue("Blacksmithy")
    if skill_value < 43:
        return ["Weapons", "Swords", "Cutlass", 0x1440]
    elif skill_value < 50:
        return ["Weapons", "Swords", "Stiletto", 0x2384]
    elif skill_value < 50:
        return ["Weapons", "Swords", "Kryss", 0x1401]
    elif skill_value < 75:
        return ["Weapons", "Swords", "Katana", 0x13FE]
    else:
        return ["Weapons", "Swords", "Katana", 0x13FE]

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

def get_item_from_container(type: int, color: int, container: int, name: str = "") -> bool:
    if FindTypeEx(type, color, container, False):
        Grab(FindItem(), 1)
        Wait(500)
        if len(name) > 0:
            log(f"{name} left in container: {FindCount()}")
        return FindTypeEx(type, color, Backpack(), False)

def tool_equipped() -> bool:
    if IsObjectExists(RhandLayer()):
        if GetType(FindItem()) == HAMMER_TYPE:
            return True

    return False

def equip_tool() -> bool:
    if FindType(HAMMER_TYPE, Backpack()):
        Equip(RhandLayer(), FindItem())
        Wait(2000)
    return tool_equipped()

def enough_resources():
    FindTypeEx(INGOTS, COLOR, Ground(), False)
    return True if FindFullQuantity() > 100 else False

def get_and_equip_tool() -> bool:
    if get_item_from_container(HAMMER_TYPE, COLOR, TOOL_CHEST, "Hammer"):
        equip_tool()

    return tool_equipped()

def craft_item(item_details: list[str]):
    item_name = item_details[-2]
    log(f"Crafting {item_name}", "DEBUG")
    if FindTypeEx(INGOTS, COLOR, Ground(), False):
        _started = dt.now()
        CancelAllMenuHooks()
        cancel_targets()
        WaitTargetObject(FindItem())
        UseObject(ObjAtLayer(RhandLayer()))
        Wait(500)
        for category in item_details[:3]:
            log(f"Selecting {category}")
            WaitMenu("What", category)
        WaitJournalLine(_started, "finished|aborted", 600000)
    Wait(500)

def smelt(item_details: list[str]):
    item_type = item_details[-1]
    while FindTypeEx(item_type, COLOR, Backpack(), False):
        _started = dt.now()
        cancel_targets()
        WaitTargetObject(FindItem())
        UseType(TONGS_TYPE, -1)
        WaitJournalLine(_started, "finished|aborted", 600000)
    if FindTypeEx(INGOTS, COLOR, Backpack(), False):
        ingots = FindItem()
        if FindTypeEx(INGOTS, COLOR, Ground(), False):
            MoveItem(ingots, -1, FindItem(), 0, 0, 0)
        else:
            DropHere(ingots)

def full_disconnect():
    SetARStatus(False)
    Disconnect()
    exit()

def init() -> None:
    SetARStatus(True)
    SetPauseScriptOnDisconnectStatus(True)
    ClearSystemJournal()
    if IsObjectExists(ObjAtLayer(RhandLayer())):
        UnEquip(RhandLayer())
        Wait(2000)
    UOSay(".autoloop 10")
    if IsObjectExists(TOOL_CHEST):
        UseObject(TOOL_CHEST)
        Wait(2000)
    else:
        log("Tool chest not found!", "CRITICAL")

if __name__ == "__main__":
    init()
    while not Dead() and Connected():
        item_to_craft = get_target_item_and_category()
        if not hungry() or not enough_resources():
            log("No food or resources!", "CRITICAL")
            #full_disconnect()

        if not tool_equipped():
            if FindType(HAMMER_TYPE, Backpack()):
                equip_tool()
            else:
                log("No tool equipped and no tool in backpack, time to get new", "DEBUG")
                get_and_equip_tool()

        craft_item(item_to_craft)
        if not FindType(TONGS_TYPE, Backpack()):
            get_item_from_container(TONGS_TYPE, -1, TOOL_CHEST, "Tongs")
        smelt(item_to_craft)

        Wait(100)



