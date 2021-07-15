from py_stealth.methods import *
from datetime import timedelta, datetime as dt
import platform
import requests
import inspect
import yaml
import os
import re

# Verbosity of log messages
LOG_VERBOSITY = 1
# Types
PICKAXE = 0x0E85
FOOD = 0x097B
CAVE_TILES = range(1339, 1358)
ORE = 0x19B9
INGOTS = 0x1BF2
COPPER_COLOR = 0x0602
TINKER_TOOLS = 0x1EBC
WEIGHT_LIMIT = MaxWeight() - 60
WEIGHT_TO_UNLOAD = MaxWeight() - 100
KEEP_TOOLS = 3
GEMS = [
    0x0F10, # Emeralds
    0x0F11, # Sapphires
    0x0F12, # Sapphires-2
    0x0F13, # Rubies
    0x0F14, # Rubies-2
    0x0F15, # Citrines
    0x0F16, # Amethysts
    0x0F17, # Amethysts-2
    0x0F18, # Tourmalines
    0x0F25, # Pieces of Amber
    0x0F30, # Diamond
    0x0F0F  # Star Sapphires
]
NEXT_TILE_MESSAGES = [
    "too far",
    "Looping aborted",
    "Looping finished",
    "You stop",
    "no ore left",
    "reach that",
    "mine that",
    "You can't see",
    "does not seem to exist"
]

# Script configuration
TILE_SEARCH_RANGE = 10

class ErrorCounter(object):

    _errors = 0

    def get_errors_count(self):
        return type(self)._errors

    def set_errors_count(self,count):
        type(self)._errors = count

    errors = property(get_errors_count, set_errors_count)

# Helper functions
def disconnect() -> None:
    SetARStatus(False)
    SetPauseScriptOnDisconnectStatus(False)
    Disconnect()
    log("Disconnected", "CRITICAL")
    exit()

def get_character_config() -> object:
    # Get only 1st word in name
    _character_name = CharName().split()[0]
    _script_filename = os.path.basename(__file__).split(".")[0]
    _config_filename = f"{_character_name}_{_script_filename}.yaml"

    # FUKKEN SHINDOWS
    if platform.system() == "Linux":
        _config_path = f"./Scripts/Crafter/Config/{_config_filename}"
    else:
        _config_path = f"../Scripts/Crafter/Config/{_config_filename}"

    log(f"Character config: {_config_path}", "INFO")

    if os.path.isfile(_config_path):
        log("Character config found", "DEBUG")
    else:
        log(f"Character config not found, expected location: {_config_path}", "CRITICAL")
        disconnect()

    with open(_config_path, "r") as _config_file:
        try:
            _config = yaml.safe_load(_config_file)["config"]
            log(f"Config file successfully loaded! {_config_path}", "DEBUG")
            return _config
        except yaml.YAMLError as _exception:
            log(f"Exception during config parsing: {_exception}", "CRITICAL")
            disconnect()



def log(message: str, level: str = "DEBUG") -> None:
    _counter = ErrorCounter()
    _verbosity_level = {
        "DEBUG":    1,
        "INFO":     2,
        "ERROR":    3,
        "CRITICAL": 4
    }

    if _verbosity_level[level] >= LOG_VERBOSITY:
        AddToSystemJournal(f"[{level}] ({inspect.stack()[1].function}) {message}")

    if level == "ERROR":
        _counter.errors =+ 1
        AddToSystemJournal(f"Error count: {_counter.errors}")

    if _counter.errors > 10:
        _counter.errors = 0
        Disconnect()


def hungry() -> bool:
    if Luck() < 90:
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
    _pickaxe = ObjAtLayer(RhandLayer())
    if IsObjectExists(_pickaxe):
        log("Pickaxe in hand exists, using Arms Lore", "DEBUG")
        cancel_targets()
        WaitTargetObject(_pickaxe)
        UseSkill("Arms Lore")
        Wait(1000)

def smelt() -> None:
    log("Weight limit reached, going to smelt ore", "DEBUG")
    if move_x_y(config["forge"]["x"], config["forge"]["y"]):
        log("Reached forge", "DEBUG")
        if FindType(ORE, Backpack()):
            for _ore in GetFoundList():
                _started = dt.now()
                UseObject(_ore)
                WaitJournalLine(_started, "You put", 10 * 1000)
                Wait(1000)
            if FindType(INGOTS, Ground()):
                for dropped_ingot in GetFoundList():
                    Grab(dropped_ingot)
                    Wait(2000)
            log("Smelting finished", "DEBUG")

def unload_to_bank() -> None:
    log("Weight limit reached, heading to bank", "DEBUG")
    if move_x_y(config["bank"]["x"], config["bank"]["y"]):
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
        if FindTypesArrayEx(GEMS+[INGOTS], [0xFFFF], [Backpack()], False):
            for _item in GetFoundList():
                MoveItem(_item, -1, _bank, 0, 0, 0)
                Wait(2000)

        if not FindType(FOOD, Backpack()) or FindQuantity() < 10:
            log("Not enought food in pack, let's get some", "DEBUG")
            if not grab_from_container(FOOD, 0x0000, 10, _bank):
                log("No food left in bank", "CRITICAL")

        craft_tools()
        statistics(_bank)
    else:
        log("Failed to reach bank", "ERROR")

def statistics(container: int) -> None:
    _container_content = {}
    _message = f"{CharName()}: \n"

    if FindTypesArrayEx(GEMS + [INGOTS], [0xFFFF], [container], False):
        for _item in GetFoundList():
            _item_tooltip = GetTooltip(_item)
            _match = re.search('^\d+\s([\w\s]+)', _item_tooltip)
            if _match:
                _item_name = _match.group(1).capitalize()
                if not _item_name in _container_content:
                    _container_content[_item_name] = GetQuantity(_item)
                else:
                    _container_content[_item_name] += GetQuantity(_item)
        _sorted_container_content = dict(sorted(_container_content.items(), key=lambda x: x[1], reverse=True))

        for _item_name, _item_qty in _sorted_container_content.items():
            _message += f"{_item_name} -> {_item_qty}\n"

        if "discord" in config and "post_statistics" in config["discord"] and config["discord"]["post_statistics"]:
            send_discord_message(_message)
        AddToSystemJournal(_message)


def grab_from_container(type: int, color: int, qty: int, container: int) -> bool:
    if FindTypeEx(type, color, container) and FindQuantity() >= qty:
        Grab(FindItem(), qty)
        Wait(1000)
        log("Got item from bank", "DEBUG")
        return True
    log("Failed to get item from bank", "ERROR")
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
        if not grab_from_container(INGOTS, COPPER_COLOR, 50, ObjAtLayer(BankLayer())):
            log("No ingots left in bank", "CRITICAL")
            disconnect()
        while Count(TINKER_TOOLS) < 2:
            craft_item("Tools", "Tinker")
            Wait(1000)
        while Count(PICKAXE) < KEEP_TOOLS:
            craft_item("Deadly", "Pickaxe")
            Wait(1000)

def check_stamina() -> None:
    if Stam() < MaxStam():
        log(f"Stamina is low, waiting for full regeneration", "DEBUG")
        while Stam() < (MaxStam() - 10):
            Wait(1000)

def move_x_y(x: int, y: int) -> bool:
    check_stamina()
    log(f"Heading to point {x}, {y}", "DEBUG")
    _try = 0
    while not newMoveXY(x, y, True, 0, True) and _try < 10:
        check_stamina()
        if newMoveXY(x, y, True, 0, True):
            log(f"Reached point {x}, {y}", "DEBUG")
            return True
        else:
            log(f"Failed to reach point {x}, {y}", "DEBUG")
            _try += 1
    return True

def send_discord_message(message: str):
    requests.post(config["discord"]["webhook_url"], json={"content": message})

def mine(tile: int, x: int, y: int, z: int) -> None:
    if move_x_y(x, y):
        log(f"Reached point {x}, {y}","DEBUG")
        Wait(1000)
        if equip_pickaxe():
            hungry()
            if Weight() >= WEIGHT_LIMIT:
                smelt()
                if Weight() >= WEIGHT_TO_UNLOAD:
                    unload_to_bank()
                    # Should use it because of 2nd floor above mine
                    move_x_y(config["start_point"]["x"], config["start_point"]["y"])
                if move_x_y(x, y):
                    log("Reached mining point", "DEBUG")
                else:
                    return

            _started = dt.now()
            # Flood protection
            if InJournalBetweenTimes("must wait|doing something", dt.now() - timedelta(minutes=1), _started) < 1:
                cancel_targets()
                arms_lore()

            cancel_targets()
            log(f"Started mining at {x}, {y}", "DEBUG")
            UseObject(ObjAtLayer(RhandLayer()))
            if WaitForTarget(2000):
                _started = dt.now()
                WaitTargetTile(tile, x, y, z)
                _minutes_waiting = 0
                while _minutes_waiting < 5:
                    Wait(60 * 1000)
                    _minutes_waiting += 1
                    log(f"Waiting for {_minutes_waiting} minutes", "DEBUG")
                    if InJournalBetweenTimes("|".join(NEXT_TILE_MESSAGES), _started, _started + timedelta(minutes=3)) > 1:
                        log("Stop-line found, breaking that shit", "DEBUG")
                        break

                log(f"Finished mining at {x}, {y}", "DEBUG")
            else:
                log(f"Failed to get target using pickaxe at {x}, {y}", "ERROR")
                return
        else:
            log("Can't equip pickaxe, heading to bank to craft some", "DEBUG")
            unload_to_bank()

if __name__ == "__main__":

    ClearSystemJournal()
    config = get_character_config()
    UOSay(".autoloop 100")
    SetARStatus(True)
    SetPauseScriptOnDisconnectStatus(True)
    SetWarMode(False)
    while not Dead() and Connected():
        move_x_y(config["start_point"]["x"], config["start_point"]["y"])
        for tile_set in find_tiles(GetX(Self()), GetY(Self()), TILE_SEARCH_RANGE):
            tile, x, y, z = tile_set
            mine(tile, x, y, z)
            Wait(500)