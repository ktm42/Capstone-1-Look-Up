from datetime import datetime, timedelta
from models import Destination
from flight_search import FlightSearch
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def deal_search():
    """Searches for deals to the destination city with a price lower than the top price"""

today = datetime.now() + timedelta(1)
six_month_out = datetime.now() + timedelta(6 * 30)

destinations = Destination.query.all()

for destination in destinations:
    flight_search = FlightSearch()

    #Get user associted with the destination
    user = User.query.get(destination.user_id)

    #Set origin city iata based on the user's base city
    ORIGIN_CITY_IATA = flight_search.iata_code(user.base_city)

    flight = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination.iata.code,
        from_time = today,
        to_time = six_month_out
    )

    if flight.price <= destination['top_price']:
        simulate_notification(
            f"Low price alert! Only ${flight.price} to fly from {flight.base_city} - {flight.origin_airport} to {flight.destination_city} - {flight.destination_airport} from {flight.out_date} to {flight.return_date}"
        )
    # if flight.price <= destination.top_price:
    #     notification_manager.send_sms(
    #         message = f"Low price alert! Only ${flight_price} to fly from {flight.base_city} -{flight.origin_airport} to {flight.destination_city} - {flight.destination_airport}from {flight.out_date} to {flight.return_date}"
    #     )

scheduler.add_job(deal_search, 'interval', days = 1, start_date = '2023-12-23 00:00:00')

#scheduler.start()