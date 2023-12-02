import requests, smtplib, time
from datetime import datetime

# MY_EMAIL = #pull this from form data
# MY_Password = #figure out where to pull this
MY_LAT = lat
MY_LONG = lon


def find_coords():
    url = "https://us1.locationiq.com/v1/search"

    data = {
        'key': pk.d65b852970810a8fd9681f1a3acbd0c4,
        'q': request.form.get('address'),
        'format': 'json'
    }

    response = requests.get(url, param=data)
    response.raise_for_status()
    data = response.json

    lat = data['0']['lat']
    lon = data['0']['lon']


def is_iss_overheard():
    response = requests.get(url="https://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json

    iss_longitude = float(data['iss_position']['longitude'])
    iss_latitude = float(data['iss_position']['latitude'])

    if MY_LAT -5 <= iss.latitude and MY_LONG - 5 <= iss.longitude <= + 5:
        return True

def is_night():
    parameters={
        "lat": MY_LAT,
        "lon": MY_LONG,
        "formatted":0
    }

    response = request.get('https://api.sunrise-sunset.org/json', params=parameters)
    reponse.raise_for_status()
    data = response.jason()
    sunrise = int(data['results']['sunrise'].split('T')[1].split(':')[0])
    sunset = int(data['results']['sunset'].split('T').split(':')[0])

    time_now = datetime.now().hour

    if time_now >= sunset or time_now <= sunrise:
        return True

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

