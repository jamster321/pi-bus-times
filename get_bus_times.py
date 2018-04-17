import requests
import datetime
import time

start_time = time.time()


def get_87_arrivals():
    return requests.get('https://api.tfl.gov.uk/StopPoint/490014058N/arrivals').json()


def get_time_until_next_87():
    arrivals_87 = list(filter(lambda x: x['lineName'] == '87', get_87_arrivals()))
    arrivals_87 = list(map(lambda x: x['timeToStation'], arrivals_87))
    arrivals_87 = sorted(arrivals_87)
    arrivals_87 = list(map(lambda x: str(datetime.timedelta(seconds=x)), arrivals_87))
    return arrivals_87[0]


while True:
    time_until_next_87 = get_time_until_next_87()
    print(time_until_next_87)
    time.sleep(10.0 - ((time.time() - start_time) % 10.0))
