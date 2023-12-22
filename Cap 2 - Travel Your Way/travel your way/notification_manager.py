class NotificationManager:
    #This class is responsible for sending notifications with the deal flight details.
    pass

    if flight_data:
        try:
            # Save the destination and flight data to the database
            new_destination = Destination(
                destination=new_destination,
                iata_code=iata_code,
                top_price=top_price,
                user=g.user
            )
            print(f'Before database commit')
            db.session.add(new_destination)
            db.session.commit()
            print(f'Database commit successful')

            # Use FlightData class to create an instance
            flight_instance = FlightData(
                price=flight_data.price,
                base_city=flight_data.base_city,
                origin_airport=flight_data.origin_airport,
                destination_city=flight_data.destination_city,
                destination_airport=flight_data.destination_airport,
                out_date=flight_data.out_date,
                return_date=flight_data.return_date
            )

            print(f'After database commit')
            flash('Destination added!')
            return redirect('/user')  # Redirect to the user homepage after adding destination
            print('Redirectin to user homepage')

        except Exception as e:
            print(f"Error during database commit: {e}")
            db.session.rollback()  # Rollback changes in case of an IntegrityError
            error = 'Error during databse commit'          
        else:
            print('Flight data is None')   
    else:
        print(f"Form errors: {form.errors}")
        print(f"CSRF Token: {form.csrf_token.data}")
        error = 'Invalid form submission'