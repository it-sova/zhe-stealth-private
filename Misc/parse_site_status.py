from os import write
from urllib.request import urlopen
import re
import platform
from datetime import datetime as dt
from time import sleep

ZHE_STATUS_URL = "https://zuluhotel.net.ua/online"

if platform.system() == "Linux":
    CSV_FILE_PATH = './zhe_site_stats.csv'
else:
    CSV_FILE_PATH = '../zhe_site_stats.csv'

def load_status_page(timeout=3):
    result_html = ''
    with urlopen(ZHE_STATUS_URL, timeout=timeout) as response:
        for line in response:
            line = line.decode('utf-8')  # Decoding the binary data to text.
            result_html += line
    # with open('status.html', 'w') as html_file:
    #     html_file.write(result_html)
    return result_html

if __name__ == "__main__":
    update_interval = 60
    while True:
        try:
            status_html = str(load_status_page())
        except Exception as e:
            print(f'[Error] During loading status page {e}')
            sleep(5)
            continue
        regex = '<font color="#453900">Online:<\/font><\/b><\/td><td align="left"><font color="#0000FF"><\/span> <b>(\d?\d+)<\/b><\/font>'
        online_first = re.findall(regex, status_html)
        regex = '<dev class="sml">Всего online: (\d?\d+)! <br>'
        online_second = re.findall(regex, status_html)
        regex = '<b class=\'dobrb\' title=\'\'>  ([a-zA-Z]+ ?[a-zA-Z]+)<\/b>'
        chars = re.findall(regex, status_html)
        
        if not (len(online_first) or len(online_second) or len(chars)):
            sleep(5)
            continue
        if abs(int(online_first[0]) - int(online_second[0])) > 2:
            print(f'{dt.now().strftime("%H:%M:%S")} Online counters differ badly {online_first[0]}/{online_second[0]}, chars[{len(chars)}]')
            update_interval = 10
        else:    
            with open(CSV_FILE_PATH, 'a') as online_stats_file:
                current_date_string = dt.now().strftime("%d-%m-%Y")
                current_time_string = dt.now().strftime("%H:%M:%S")
                online_stats_file.write(f'{current_date_string};{current_time_string};{online_first};{chars};\n')
                print(f'[Debug] data written, online: {online_first[0]}/{online_second[0]}, chars[{len(chars)}]')
                update_interval = 60

        sleep(update_interval)



        # if len(chars) != online_first:
        #     print(f'chars and online_first doesn\'t match')
        # if len(chars) != online_second:
        #     print(f'chars and online_second doesn\'t match')

        # print(f'online_first = {online_first}')
        # print(f'online_second = {online_second}')
        # print(f'chars[{len(chars)}] = {chars}')