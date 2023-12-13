import requests, smtplib, time
from datetime import datetime
from models import Coordinates

# MY_EMAIL = #pull this from form data
# MY_Password = #figure out where to pull this
MY_LAT = None
MY_LON = None

def find_coords(address, user):
    global MY_LAT, MY_LON

    url = "https://us1.locationiq.com/v1/search"

    data = {
        'key': 'pk.d65b852970810a8fd9681f1a3acbd0c4',
        'q': address,
        'format': 'json'
    }

    response = requests.get(url, params=data)
    response.raise_for_status()
    data = response.json()

    MY_LAT = float(data[0]['lat'])
    MY_LON = float(data[0]['lon'])
        
    coordinates = Coordinates.log_coords(
        latitude=MY_LAT,
        longitude= MY_LON,
        user=user
    )

def is_iss_overhead(lat, lon):
    response = requests.get(url="https://api.wheretheiss.at/v1/satellites/25544")
    response.raise_for_status()
    data = response.json()

    iss_longitude = float(data['longitude'])
    iss_latitude = float(data['latitude'])

    if lat -5 <= iss_latitude and lon - 5 <= iss_longitude <= + 5:
        parameters={
            "lat": lat,
            "lon": lon,
            "formatted":0
        }

        response = requests.get('https://api.sunrise-sunset.org/json', params=parameters)
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
# while True:
#     time.sleep(60)
#     if is_iss_overheard() and is_night():
#         connection = smtplib.SMTP('smtp.gmail.com')
#         connection.starttls()
#         connection.login(MY_EMAIL, MY_PASSWORD)
#         connection.sendmail(
#             from_addr=MY_EMAIL,
#             to_addr=MY_EMAIL,
#             msg="Subject: Go Outside/n/nLook up to see the ISS passing by."
#         )

