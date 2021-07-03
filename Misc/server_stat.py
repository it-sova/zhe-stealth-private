from py_stealth.methods import *

from datetime import datetime as dt
from datetime import timedelta as td
import platform
import re

if platform.system() == "Linux":
    CSV_FILE_PATH = './zhe_stats.csv'
else:
    CSV_FILE_PATH = '../zhe_stats.csv'

# ^\D+(\d+).+$
if __name__ == "__main__":
    while (True):
        before_timestamp = dt.now()
        sysload_line_id = -1
        UOSay('.online')
        while sysload_line_id < 0:
            sysload_line_id = InJournalBetweenTimes('Sys. Load', dt.now()-td(seconds=0.5), dt.now())
            Wait(50)
        after_timestamp = dt.now()
        
        online_line_id = InJournalBetweenTimes('players online!', dt.now()-td(seconds=0.5), dt.now())
        sys_load_line = Journal(sysload_line_id)
        online_line = Journal(online_line_id)

        sys_load = re.search('\d+', sys_load_line)
        players_online = re.search('\d+', online_line)
        
        latency = after_timestamp-before_timestamp
        latency_s = latency.seconds
        latency_ms = latency.microseconds
        current_date_string = after_timestamp.strftime("%d-%m-%Y")
        current_time_string = after_timestamp.strftime("%H:%M:%S")

        # print(f'time: {current_time}')
        # print(f'latency {(after_timestamp-before_timestamp)}')
        # print(f'sys_load {sys_load.group(0)}%')
        # print(f'players_online {players_online.group(0)}')
        with open(CSV_FILE_PATH, 'a') as csv_file:
            csv_file.write(f"{current_date_string};{current_time_string};{sys_load.group(0)};{players_online.group(0)};{latency};{latency_s};{latency_ms};\n")           
        Wait(10000)