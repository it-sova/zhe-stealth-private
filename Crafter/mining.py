from py_stealth.methods import *
from datetime import datetime as dt
import inspect
import yaml
import os
import re

# Verbosity of log messages
LOG_VERBOSITY = 1

# Types
PICKAXE = 0x0E85
FOOD = 0x097B
CAVE_TILES = range(1339, 1359)
ORE = 0x19B9
INGOTS = 0x1BF2
COPPER_COLOR = 0x0602
TINKER_TOOLS = 0x1EBC
WEIGHT_LIMIT = MaxWeight() - 20
WEIGHT_TO_UNLOAD = MaxWeight() - 50
KEEP_TOOLS = 5

NEXT_TILE_MESSAGES = [
    "Too far",
    "Looping aborted",
    "reach that",
    "mine that"
]

# Script configuration
TILE_SEARCH_RANGE = 10

# Helper functions
def disconnect() -> None:
    SetARStatus(False)
    SetPauseScriptOnDisconnectStatus(False)
    #Disconnect()
    log("Disconnected", "CRITICAL")

def get_character_config() -> object:
    # Get only 1st word in name
    _character_name = CharName().split()[0]
    _script_filename = os.path.basename(__file__).split(".")[0]
    _config_filename = f"{_character_name}_{_script_filename}.yaml"
    log(f"Character config: {_config_filename}", "INFO")

    if os.path.isfile(f"./Scripts/Crafter/Config/{_config_filename}"):
        log("Character config found", "DEBUG")
    else:
        log(f"Character config not found, expected location: ./Config/{_config_filename}", "CRITICAL")
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
    _verbosity_level = {
        "DEBUG":    1,
        "INFO":     2,
        "ERROR":    3,
        "CRITICAL": 4
    }

    if _verbosity_level[level] >= LOG_VERBOSITY:
        AddToSystemJournal(f"[{level}] ({inspect.stack()[1].function}) {message}")


def hungry() -> bool:
    if Luck() < 85:
        if Count(FOOD) > 2:
            UseType(FOOD, 0x0000)
            Wait(1000)
            log(f"Food left in backpack: {Count(FOOD)}", "INFO")
            return True
        else:
            log("No more food left in backpack!", "ERROR")
            return False

# Script specific functions
def find_tiles(center_x: int, center_y: int, radius: int) -> set[int, int, int, int]:
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    for _tile in CAVE_TILES:
        _tiles_coordinates += GetStaticTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), _tile)
    log(f"Found {str(len(_tiles_coordinates))} tiles", "INFO")
    return _tiles_coordinates

def equip_pickaxe() -> bool:
    if not ObjAtLayer(RhandLayer()):
        if Count(PICKAXE) > 1:
            Equipt(RhandLayer(), PICKAXE)
            log(f"Pickaxe equipped, pickaxes left in backpack: {Count(PICKAXE)}", "DEBUG")
            return True
        else:
            log("No more pickaxes left in backpack", "INFO")
            return False
    return True

def cancel_targets() -> None:
    if TargetPresent():
        CancelTarget()
    CancelWaitTarget()

def arms_lore() -> None:
    cancel_targets()
    WaitTargetObject(ObjAtLayer(RhandLayer()))
    UseSkill("Arms Lore")
    Wait(1000)

def smelt() -> None:
    if FindType(ORE, Backpack()):
        for _ore in GetFoundList():
            _started = dt.now()
            UseObject(_ore)
            WaitJournalLine(_started, "You put", 1000)
        log("Smelting finished", "DEBUG")
    else:
        log("Weight limit reached but no ore found in pack", "CRITICAL")
        disconnect()

def unload_to_bank() -> None:
    _bank = ObjAtLayer(BankLayer())
    if newMoveXY(config["bank"]["x"], config["bank"]["y"], True, 0, True):
        log("Reached bank", "DEBUG")
        UseObject(Backpack())
        Wait(1000)
        _try = 0
        while LastContainer() != _bank:
            _try += 1
            if _try > 10:
                log("Failed to open bank 10 times a row", "CRITICAL")
                disconnect()
            UOSay("bank")
            Wait(1000)
        log("Bank opened", "DEBUG")
        if FindType(INGOTS, Backpack()):
            for _ingots in GetFoundList():
                MoveItem(_ingots, -1, _bank, 0, 0, 0)
                Wait(2000)
        craft_tools()
        statistics(_bank)
    else:
        log("Failed to reach bank", "ERROR")

def statistics(container: int) -> None:
    AddToSystemJournal("==================")
    if FindType(INGOTS, container):
        for _ingot in GetFoundList():
            _ingot_tooltip = GetTooltip(_ingot)
            _match = re.search('\d+\s([\w\s]+)', _ingot_tooltip)
            if _match:
                _ingot_name = _match.group(1).capitalize()
                AddToSystemJournal(f"{_ingot_name}: {FindFullQuantity()}")
    AddToSystemJournal("==================")


def grab_from_container(type: int, color: int, qty: int, container: int) -> bool:
    if FindTypeEx(INGOTS, COPPER_COLOR, container):
        Grab(FindItem(), 100)
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
        AutoMenu("What", category)
        AutoMenu("What", item)
        WaitTargetObject(FindItem())
        UseType(TINKER_TOOLS, -1)
        WaitJournalLine(_started, "Looping finished", 15 * 1000)
    UOSay(".autoloop 100")
    Wait(500)

def craft_tools() -> None:
    if Count(TINKER_TOOLS) < 2 or Count(PICKAXE) < KEEP_TOOLS:
        log("Not enought tools in pack, let's craft some", "DEBUG")
        grab_from_container(INGOTS, COPPER_COLOR, 100, ObjAtLayer(BankLayer()))
        while Count(TINKER_TOOLS) < 2:
            craft_item("Tools", "Tinker")
            Wait(1000)
        while Count(PICKAXE) < KEEP_TOOLS:
            craft_item("Deadly", "Pickaxe")
            Wait(1000)


def mine(tile: int, x: int, y: int, z: int) -> None:
    if newMoveXY(x, y, True, 0, True):
        log(f"Reached point {x}, {y}","DEBUG")
        if equip_pickaxe():
            if Weight() >= WEIGHT_LIMIT:
                log("Weight limit reached, going to smelt ore", "DEBUG")
                if newMoveXY(config["forge"]["x"], config["forge"]["y"], True, 0, True):
                    log("Reached forge", "DEBUG")
                    smelt()
                    if Weight() >= WEIGHT_TO_UNLOAD:
                        log("Weight limit reached, heading to bank", "DEBUG")
                        unload_to_bank()
                    if newMoveXY(x, y, True, 0, True):
                        log("Reached mining point", "DEBUG")
                    else:
                        log("Failed to return to mining point", "ERROR")
                        return
            arms_lore()
            _started = dt.now()
            cancel_targets()
            UseObject(ObjAtLayer(RhandLayer()))
            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetTile(tile, x, y, z)
                WaitJournalLine(_started, "|".join(NEXT_TILE_MESSAGES), 10 * 60 * 1000)
        else:
            log("Can't equip pickaxe, heading to bank to craft some", "DEBUG")
            unload_to_bank()


if __name__ == "__main__":
    ClearSystemJournal()
    UOSay(".autoloop 100")
    SetARStatus(True)
    SetPauseScriptOnDisconnectStatus(True)
    SetWarMode(False)
    config = get_character_config()
    newMoveXY(config["start_point"]["x"], config["start_point"]["y"], True, 0, True)
    while not Dead() and Connected():
        for tile_set in find_tiles(GetX(Self()), GetY(Self()), TILE_SEARCH_RANGE):
            tile, x, y, z = tile_set
            mine(tile, x, y, z)