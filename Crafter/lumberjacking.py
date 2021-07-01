from py_stealth.methods import *
from datetime import datetime as dt
import requests
import inspect
import yaml
import os
import re

# Verbosity of log messages
LOG_VERBOSITY = 1

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/858974853516230706/-KMww3sv9nxZLR8xZS8TSzzxaZt_FMREP-_z6zN09TFVMwOzzsJvmfrwz8KD2EkIpUPb"
# Types
HATCHET =0x0F43
FOOD = 0x097B
TREE_TILES = [
    3230,3272,3274,3275,
    3276,3277,3278,3280,
    3281,3283,3284,3286,
    3287,3288,3289,3290,
    3291,3292,3293,3294,
    3295,3296,3299,3300,
    3302,3303,3384,3385,
    3391,3392,3394,3395,
    3417,3440,3460
]
LOGS = 0x1BDD
INGOTS = 0x1BF2
COPPER_COLOR = 0x0602
TINKER_TOOLS = 0x1EBC
WEIGHT_TO_UNLOAD = MaxWeight() - 60
KEEP_TOOLS = 3
NEXT_TILE_MESSAGES = [
    "too far",
    "Looping aborted",
    "You stop",
    "reach that",
    "mine that",
    "does not seem to exist"
]

# Script configuration
TILE_SEARCH_RANGE = 15

# Helper functions
def disconnect() -> None:
    SetARStatus(False)
    SetPauseScriptOnDisconnectStatus(False)
    #Disconnect()
    log("Disconnected", "CRITICAL")
    exit()

def get_character_config() -> object:
    # Get only 1st word in name
    _character_name = CharName().split()[0]
    _script_filename = os.path.basename(__file__).split(".")[0]
    _config_filename = f"{_character_name}_{_script_filename}.yaml"
    log(f"Character config: {_config_filename}", "INFO")

    if os.path.isfile(f"./Scripts/Crafter/Config/{_config_filename}"):
        log("Character config found", "DEBUG")
    else:
        log(f"Character config not found, expected location: ./Scripts/Crafter/Config/{_config_filename}", "CRITICAL")
        disconnect()

    with open(f"./Scripts/Crafter/Config/{_config_filename}", "r") as _config_file:
        try:
            _config = yaml.safe_load(_config_file)["config"]
            log(f"Config file successfully loaded! {_config}", "DEBUG")
            return _config
        except yaml.YAMLError as _exception:
            log(f"Exception during config parsing: {_exception}", "CRITICAL")
            disconnect()



def log(message: str, level: str = "DEBUG") -> None:
    global errors;
    _verbosity_level = {
        "DEBUG":    1,
        "INFO":     2,
        "ERROR":    3,
        "CRITICAL": 4
    }

    if _verbosity_level[level] >= LOG_VERBOSITY:
        AddToSystemJournal(f"[{level}] ({inspect.stack()[1].function}) {message}")

    if level == "ERROR":
        errors =+ 1

    if errors > 10:
        errors = 0
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

# Script specific functions
def find_tiles(center_x: int, center_y: int, radius: int) -> set[int, int, int, int]:
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    for _tile in TREE_TILES:
        _tiles_coordinates += GetStaticTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), _tile)
    log(f"Found {str(len(_tiles_coordinates))} tiles", "INFO")
    return _tiles_coordinates

def equip_hatchet() -> bool:
    if not ObjAtLayer(RhandLayer()):
        if Count(HATCHET) > 1:
            Equipt(RhandLayer(), HATCHET)
            log(f"Hatchet equipped, pickaxes left in backpack: {Count(HATCHET)}", "DEBUG")
            return True
        else:
            log("No more hatchets left in backpack", "INFO")
            return False
    return True

def cancel_targets() -> None:
    if TargetPresent():
        CancelTarget()
    CancelWaitTarget()

def arms_lore() -> None:
    _hatchet = ObjAtLayer(RhandLayer())
    if IsObjectExists(_hatchet):
        log("Hatchet in hand exists, using Arms Lore", "DEBUG")
        cancel_targets()
        WaitTargetObject(_hatchet)
        UseSkill("Arms Lore")
        Wait(1000)

def unload_to_bank() -> None:
    if newMoveXY(config["bank"]["x"], config["bank"]["y"], True, 0, True):
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
                disconnect()
            UOSay("bank")
            Wait(1000)
        _bank = ObjAtLayer(BankLayer())
        log("Bank opened", "DEBUG")
        if FindTypesArrayEx([LOGS], [0xFFFF], [Backpack()], False):
            for _item in GetFoundList():
                MoveItem(_item, -1, _bank, 0, 0, 0)
                Wait(2000)
        craft_tools()
        statistics(_bank)
    else:
        log("Failed to reach bank", "ERROR")

def statistics(container: int) -> None:
    AddToSystemJournal("==================")
    if FindTypesArrayEx([LOGS], [0xFFFF], [container], False):
        for _item in GetFoundList():
            _item_tooltip = GetTooltip(_item)
            _match = re.search('^\d+\s([\w\s]+)', _item_tooltip)
            if _match:
                _item_name = _match.group(1).capitalize()
                AddToSystemJournal(f"{_item_name}: {GetQuantity(_item)}")
    AddToSystemJournal("==================")


def grab_from_container(type: int, color: int, qty: int, container: int) -> bool:
    if FindTypeEx(type, color, container) and FindQuantity >= qty:
        Grab(FindItem(), qty)
        Wait(1000)
        log("Got ingots from bank", "DEBUG")
        return True
    log("Failed to get ingots from bank", "ERROR")
    return False


def craft_item(category: str, item: str) -> None:
    UOSay(".autoloop 1")
    Wait(500)
    log(f"Crafting {item}", "DEBUG")
    if FindTypeEx(INGOTS, COPPER_COLOR, Backpack()):
        _started = dt.now()
        CancelAllMenuHooks()
        cancel_targets()
        WaitMenu("What", category)
        WaitMenu("What", item)
        WaitTargetObject(FindItem())
        UseType(TINKER_TOOLS, -1)
        WaitJournalLine(_started, "Looping finished", 15 * 1000)
    UOSay(".autoloop 100")
    Wait(500)

def craft_tools() -> None:
    if Count(TINKER_TOOLS) < 2 or Count(HATCHET) < KEEP_TOOLS:
        log("Not enought tools in pack, let's craft some", "DEBUG")
        if not FindTypeEx(INGOTS, COPPER_COLOR, Backpack()) or FindQuantity() < 30:
            log("Not enought ingots in pack, let's get some", "DEBUG")
            grab_from_container(INGOTS, COPPER_COLOR, 50, ObjAtLayer(BankLayer()))
        while Count(TINKER_TOOLS) < 2:
            craft_item("Tools", "Tinker")
            Wait(1000)
        while Count(HATCHET) < KEEP_TOOLS:
            craft_item("Deadly", "Hatchet")
            Wait(1000)


def chop(tile: int, x: int, y: int, z: int) -> None:
    if newMoveXYZ(x, y, z, 1, 0, True):
        log(f"Reached point {x}, {y}","DEBUG")
        if equip_hatchet():
            hungry()
            if Weight() >= WEIGHT_TO_UNLOAD:
                log("Weight limit reached, heading to bank", "DEBUG")
                unload_to_bank()
                if newMoveXY(x, y, True, 0, True):
                    log("Reached chopping point", "DEBUG")
                else:
                    log("Failed to return to chopping point", "ERROR")
                    return
            arms_lore()
            _started = dt.now()
            cancel_targets()
            log(f"Started chopping at {x}, {y}", "DEBUG")
            UseObject(ObjAtLayer(RhandLayer()))
            if WaitForTarget(2000):
                WaitTargetTile(tile, x, y, z)
                WaitJournalLine(_started, "|".join(NEXT_TILE_MESSAGES), 6 * 60 * 1000)
                log(f"Finished chopping at {x}, {y}", "DEBUG")
            else:
                log(f"Failed to get target using hatchet at {x}, {y}", "ERROR")
                return
        else:
            log("Can't equip hatchet, heading to bank to craft some", "DEBUG")
            unload_to_bank()
    else:
        log(f"Cant get to chopping point {x},{y},{z}","ERROR")

if __name__ == "__main__":
    errors = 0
    ClearSystemJournal()
    UOSay(".autoloop 100")
    SetARStatus(True)
    SetMoveOpenDoor(True)
    SetWarMode(False)
    SetPauseScriptOnDisconnectStatus(True)
    config = get_character_config()
    while not Dead() and Connected():
        if newMoveXY(config["start_point"]["x"], config["start_point"]["y"], True, 0, True):
            for _point in config["points"]:
                point_x, point_y = _point
                log(f"Point: {point_x}, {point_y}", "DEBUG")
                if newMoveXY(point_x, point_y, True, 0, True):
                    log(f"Reached point: {point_x}, {point_y}", "DEBUG")
                    for tile_set in find_tiles(GetX(Self()), GetY(Self()), TILE_SEARCH_RANGE):
                        tile, x, y, z = tile_set
                        chop(tile, x, y, z)
                else:
                    log("Failed to get to point: {point_x}, {point_y}", "ERROR")
                    break
        else:
            log("Failed to get to starting point! Overload?", "ERROR")
            Wait(2 * 60 * 1000)