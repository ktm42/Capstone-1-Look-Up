import requests
from datetime import datetime

MY_LAT = None
MY_LON = None

def find_coords():
    global MY_LAT, MY_LON

    url = "https://us1.locationiq.com/v1/search"

    data = {
        'key': 'pk.d65b852970810a8fd9681f1a3acbd0c4',  # Replace with your API key
        'q': '1333 Woodland DR SW Rochester MN 55902',    # Replace with the address you want to search
        'format': 'json'
    }

    response = requests.get(url, params=data)
    response.raise_for_status()
    data = response.json()

    MY_LAT = float(data[0]['lat'])
    MY_LON = float(data[0]['lon'])

    return MY_LAT, MY_LON

def is_iss_overhead():
    response = requests.get(url="https://api.wheretheiss.at/v1/satellites/25544")
    print(f"iss overhead response = {response.text}")
    response.raise_for_status()
    data = response.json()

    iss_longitude = float(data['longitude'])
    iss_latitude = float(data['latitude'])

    if MY_LAT -5 <= iss_latitude and MY_LON - 5 <= iss_longitude <= + 5:
        return True

def is_night():
    parameters={
        "lat": MY_LAT,
        "lon": MY_LON,
        "formatted":0
    }

    response = requests.get('https://api.sunrise-sunset.org/json', params=parameters)
    print(f"is night response = {response.text}")
    response.raise_for_status()
    data = response.json()

    sunrise = data['results']['sunrise']
    sunset = data['results']['sunset']

    time_sunrise = int(sunrise.split('T')[1].split(':')[0])
    time_sunset = int(sunset.split('T')[1].split(':')[0])

    time_now = datetime.now().hour

    if time_now >= time_sunset or time_now <= time_sunrise:
        return True
    return False

print('Coordinates:', find_coords())

print('ISS overhead:', is_iss_overhead())

print('Is night:', is_night())

