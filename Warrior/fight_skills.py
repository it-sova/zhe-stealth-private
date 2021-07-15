#from py_stealth.methods import AddToSystemJournal, BandageSelf, CancelTarget, CancelWaitTarget, Count, Equip, FindItem, FindType, FindTypeEx, GetFoundList, GetHP, IsObjectExists, LhandLayer, ObjAtLayer, SetFindDistance, SetWarMode, TargetPresent, UOSay, UseSkill, Wait, WaitForTarget, WaitJournalLine, WaitTargetObject, WarMode
from py_stealth.methods import *
import inspect
from datetime import datetime as dt
import platform
import inspect
import yaml
import os

FOOD = 0x097B
BANDAGES = 0x0E21
EQUIP_CHEST = 0x4C18AFB3


def get_character_config() -> object:
    # Get only 1st word in name
    _character_name = CharName().split()[0]
    _script_filename = os.path.basename(__file__).split(".")[0]
    _config_filename = f"{_character_name}_{_script_filename}.yaml"

    # FUKKEN SHINDOWS
    if platform.system() == "Linux":
        _config_path = f"./Scripts/Warrior/Config/{_config_filename}"
    else:
        _config_path = f"../Scripts/Warrior/Config/{_config_filename}"

    log(f"Character config: {_config_path}", "INFO")

    if os.path.isfile(_config_path):
        log("Character config found", "DEBUG")
    else:
        log(f"Character config not found, expected location: {_config_path}", "CRITICAL")
        full_disconnect()

    with open(_config_path, "r") as _config_file:
        try:
            _config = yaml.safe_load(_config_file)["config"]
            log(f"Config file successfully loaded! {_config_path}", "DEBUG")
            return _config
        except yaml.YAMLError as _exception:
            log(f"Exception during config parsing: {_exception}", "CRITICAL")
            full_disconnect()

def log(message: str, level: str = "DEBUG") -> None:
    _verbosity_level = {
        "DEBUG":    1,
        "INFO":     2,
        "ERROR":    3,
        "CRITICAL": 4
    }

    if _verbosity_level[level] >= 1:
        AddToSystemJournal(f"[{level}] ({inspect.stack()[1].function}) {message}")


def hungry(container: int) -> bool:
    if Luck() < 90:
        if FindType(FOOD, container):
            if FindFullQuantity() > 20:
                UseObject(FindItem())
                Wait(1000)
                log(f"Food left in container: {FindFullQuantity()}", "INFO")
            else:
                log("No more food left in backpack!", "ERROR")
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
            Wait(100)
            _try += 1
            if _try >= 10:
                log("Failed to open tool checst 10 times a row", "CRITICAL")
                full_disconnect()
    else:
        log("Container not found!", "CRITICAL")

def get_item_from_container(type: int, color: int, container: int, name: str = "") -> bool:
    open_container(container)
    if FindTypeEx(type, color, container, False):
        Grab(FindItem(), 1)
        Wait(1000)
        if len(name) > 0:
            log(f"{name} left in container: {FindCount()}")
        return FindTypeEx(type, color, Backpack(), False)

def to_safety():
    newMoveXY(config["start_point"]["x"], config["start_point"]["y"], True, 0, True)

def to_start():
    newMoveXY(config["start_point"]["x"], config["start_point"]["y"], True, 0, True)

def equip_item_on_layer(type: int, layer: int, name: str = ""):
    if not ObjAtLayer(layer):
        if FindType(type):
            Equip(layer, FindItem())
            Wait(2000)
        else:
            if get_item_from_container(type, -1, EQUIP_CHEST, name):
                print(f"Rearm {name}")
                equip_item_on_layer(type, layer)
            else:
                log("Unable to get shield from container!")



def heal(threshold: int):
    heal_at = MaxHP() / 100 * threshold
    if HP() <= heal_at:
        _start = dt.now()
        if FindType(BANDAGES, Ground()):
            WaitTargetSelf()
            UseObject(FindItem())
            WaitJournalLine(_start, "Bloody Bandages|cure|poison", 10000)
        else:
            log("No bandages found")


if __name__ == "__main__":
    UnEquip(LhandLayer())
    UnEquip(RhandLayer())
    SetFindDistance(3)
    SetARStatus(True)
    ClearSystemJournal()
    config = get_character_config()
    combat = config["combat"]
    to_start()
    loop = 0
    while not Dead() and Connected():
        heal(combat["healing_threshold"])

        if not combat["two_handed"]:
            equip_item_on_layer(combat["weapon"], RhandLayer(), "Weapon")
            equip_item_on_layer(combat["shield"], LhandLayer(), "Shield")
        else:
            equip_item_on_layer(combat["weapon"], LhandLayer(), "Weapon")

        if IsObjectExists(combat["target"]):
            Attack(combat["target"])

        if HP() < 40:
            to_safety()
            while HP() < 40:
                heal(combat["healing_threshold"])
            to_start()
        loop += 1
        if loop > 20:
            hungry(Ground())
            loop = 0
        Wait(1000)




