import requests
from flight_data import FlightData
from datetime import datetime, timedelta
import json


TEQUILA_ENDPOINT = "https://tequila-api.kiwi.com"
TEQUILA_API_KEY = 'R10dZeAww04eiiIc9UbcuVsiD4UpYYCQ'


class FlightSearch:

    def iata_code(self, city_name):
        location_endpoint = f"{TEQUILA_ENDPOINT}/locations/query"
        headers = {"apikey": TEQUILA_API_KEY}
        query = {"term": city_name, "location_types": "city"}
        response = requests.get(url=location_endpoint, headers=headers, params=query)
        results = response.json()["locations"]
        code = results[0]["code"]
        return code

    def check_flights(self, base_city, iata_code, from_time, to_time):
        headers = {"apikey": TEQUILA_API_KEY}
        query = {
            "fly_from": base_city,
            "fly_to": iata_code,
            "date_from": from_time.strftime("%d/%m/%Y"),
            "date_to": to_time.strftime("%d/%m/%Y"),
            "nights_in_dst_from": 7,
            "nights_in_dst_to": 28,
            "one_for_city": 1,
            "max_stopovers": 0,
            "curr": "USD"
        }

        response = requests.get(
            url=f"{TEQUILA_ENDPOINT}/search",
            headers=headers,
            params=query,
        )

        flight_data = None
        
        try:
            data = response.json()["data"][0]
            route = data["route"][0]
            
            flight_data = FlightData(
                price=data["price"],
                base_city=route["cityFrom"],
                origin_airport=route["flyFrom"],
                destination_city=route["cityTo"],
                destination_airport=route["flyTo"],
                out_date=datetime.utcfromtimestamp(route["dTime"]).strftime('%Y-%m-%d'),
                return_date=datetime.utcfromtimestamp(data["route"][1]["dTime"]).strftime('%Y-%m-%d')
            )
            print(f"{flight_data.destination_city}: ${flight_data.price}")

        except KeyError as e:
            response_text = response.content.decode('utf-8')
            print(f"Unexpected response format. {e}. Response: {response_text}")

        
            
        

