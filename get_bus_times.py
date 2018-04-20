import sys
import requests
import datetime
import time
import scrollphat
import RPi.GPIO as GPIO

print('Pi Bus Times Started')

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

start_time = time.time()

scrollphat.set_brightness(2)
scrollphat.clear()

lines = [
    {
        'stop_point': '490011360E',
        'line_name': '345',
        'destination': 'Peckham'
    },
    {
        'stop_point': '490014058N',
        'line_name': '87',
        'destination': 'Aldwych'
    }
]

selected_line_index = 0;

REFRESH_TIMEOUT = 45.0
SLEEP_TIMEOUT = 600.0
LOADING_TEXT = ' ...'
SCROLL_SPEED = 0.07

def get_selected_line():
    return lines[selected_line_index]

def seconds_to_minutes(seconds):
    return int((seconds % 3600) / 60)

def get_arrival_times(stop_point, line_name):
    try:
        arrivals = requests.get('https://api.tfl.gov.uk/StopPoint/' + stop_point + '/arrivals').json()
    except:
        print('error')
    arrivals = list(filter(lambda x: x['lineName'] == line_name, arrivals))
    arrivals = list(map(lambda x: x['timeToStation'], arrivals))
    arrivals = sorted(arrivals)
    arrivals = list(map(lambda x: seconds_to_minutes(x), arrivals))
    return arrivals

def concat_arrival_times(arrivals):
    arrivals = list(map(lambda x: str(x) + 'min', arrivals))
    return ' - '.join(arrivals)

def update_timer(timeout):
    return timeout - ((time.time() - start_time) % timeout)

def button_pressed(button):
    return button == False

def scroll_display():
    scrollphat.scroll()
    time.sleep(SCROLL_SPEED)

def show_next_line():
    selected_line_index = (selected_line_index + 1) % len(lines)

while True:
    scrollphat.clear()
    if button_pressed(GPIO.input(17)):
        sleep_timer = SLEEP_TIMEOUT

        while int(sleep_timer) > 0:
            sleep_timer = update_timer(SLEEP_TIMEOUT)
            refresh_timer = REFRESH_TIMEOUT

            scrollphat.clear()
            scrollphat.write_string(LOADING_TEXT, 0)

            selected_line = get_selected_line()
            arrival_times = get_arrival_times(selected_line['stop_point'], selected_line['line_name'])
            concat_arrivals = concat_arrival_times(arrival_times)

            scrollphat.clear()
            scrollphat.write_string(
                ' ' + selected_line['line_name'] + 
                ' ' + selected_line['destination'] + 
                ' ' + concat_arrivals + ' -  ')

            while int(refresh_timer) > 0:
                refresh_timer = update_timer(REFRESH_TIMEOUT)
                scroll_display()
                if button_pressed(GPIO.input(17)):
                    show_next_line()
                    break
