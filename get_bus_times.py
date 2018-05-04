import sys
import requests
import time
import scrollphathd
import RPi.GPIO as GPIO
import signal
import json

REFRESH_TIMEOUT = 45.0
SLEEP_TIMEOUT = 900.0
LOADING_TEXT = '...'
SCROLL_SPEED = 0.03
APP_ID = ''
APP_KEY = ''

bus_lines_json_filename = sys.argv[1]

with open(bus_lines_json_filename) as bus_lines_json:    
    bus_lines = json.load(bus_lines_json)

bus_lines.insert(0, {})

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
start_time = time.time()
selected_line_index = 0;
scrollphathd.set_brightness(0.2)

print('Pi Bus Times Started')

def get_selected_line():
    return bus_lines[selected_line_index]

def seconds_to_minutes(seconds):
    return int((seconds % 3600) / 60)

def get_arrival_times(stop_point, line_name):
    print('getting arrivals')
    arrivals = []
    try:
        arrivals = requests.get('https://api.tfl.gov.uk/StopPoint/' + stop_point + '/arrivals' +
            '?app_id=' + APP_ID + '&app_key=' + APP_KEY).json()
        arrivals = list(filter(lambda x: x['lineName'] == line_name, arrivals))
        arrivals = list(map(lambda x: x['timeToStation'], arrivals))
        arrivals = sorted(arrivals)
        arrivals = list(map(lambda x: seconds_to_minutes(x), arrivals))
    except:
        print('error')

    return arrivals

def concat_arrival_times(arrivals):
    arrivals = list(map(lambda x: str(x) + 'min', arrivals))
    return ' '.join(arrivals)

def update_timer(timeout):
    return timeout - ((time.time() - start_time) % timeout)

def button_pressed(button):
    return button == False

def scroll_display():
    scrollphathd.show()
    scrollphathd.scroll()
    time.sleep(SCROLL_SPEED)

def debounce_button():
    while button_pressed(GPIO.input(17)):
        time.sleep(0.01)

def show_string(text):
    scrollphathd.clear()
    scrollphathd.write_string(text, 0)
    scrollphathd.show()

while True:
    sleep_timer = SLEEP_TIMEOUT

    while int(sleep_timer) > 0:
        sleep_timer = update_timer(SLEEP_TIMEOUT)

        if selected_line_index != 0:
            selected_line = get_selected_line()
            arrival_times = get_arrival_times(selected_line['stop_point'], selected_line['line_name'])
            concat_arrivals = concat_arrival_times(arrival_times)

            show_string(
                ' ' + selected_line['line_name'] + 
                ' ' + selected_line['destination'] + 
                ' ' + concat_arrivals + ' -')
        else:
            scrollphathd.clear()

        refresh_timer = REFRESH_TIMEOUT

        while int(refresh_timer) > 0:
            refresh_timer = update_timer(REFRESH_TIMEOUT)
            scroll_display()

            if button_pressed(GPIO.input(17)):
                debounce_button()
                selected_line_index = (selected_line_index + 1) % len(bus_lines)

                if selected_line_index != 0:
                    show_string(LOADING_TEXT)

                print('selected line ' + str(selected_line_index))
                break
