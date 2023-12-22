import os

from flask import Flask, render_template, redirect, url_for, session, request, flash, g, jsonify
from datetime import datetime, timedelta
from forms import LoginForm, RegForm, AddDestinationForm, EditUserForm
from flight_search import FlightSearch
from flight_data import FlightData
from models import db, connect_db, bcrypt, User, Destination
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, template_folder='templates')
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql:///travel_your_way')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "itsasecret")

bcrypt.init_app(app) 
connect_db(app)

with app.app_context():
    db.drop_all()
    db.session.commit()
    
with app.app_context():
    db.create_all()
    
CURR_USER_KEY = 'user_id'

@app.before_request
def add_user_to_g():
    """If logged in, add the current user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Logs in user"""

    session[CURR_USER_KEY] = user.id 

def do_logout():
    """Logs out user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Shows form for user to register, handles submission, adds info to database and redirects to login. If the form is not valid, present form.  If username already exists, flash message and re-present form"""
    
    error = None

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = RegForm()
       
    if form.validate_on_submit():
        try:
            user = User.register(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            username = form.username.data,
            password = form.password.data,             
        ) 
            db.session.add(user)
            db.session.commit()
    
            do_login(user)

            return redirect('/user')
    
        except IntegrityError as e:
            db.session.rollback()
            error = f'Username taken, please try another'
            return render_template('register.html', form=form, error=error)
    else:
        return render_template('register.html', form=form)
      
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles login"""

    form = LoginForm()

    error = None

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        
        if user:
            do_login(user)
            return redirect('/user')
        else:
            error = 'Invalid username/password. Please try again.'
              
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
def logout():
    """Handles user logout"""

    do_logout()

    flash(f'Logout successful')
    return redirect('/')

@app.route('/user', methods=['GET', 'POST'])
def user_homepage():
    """Shows user list of destinations and buttons to complete other tasks"""

    error = None

    if not g.user:
        error = 'Unauthorized Access'
        return redirect('/')

    else:
        user_destinations = g.user.destinations

    form = AddDestinationForm()
    
    return render_template('user.html', form=form, user_destinations=user_destinations, error=error)

@app.route('/add_destination', methods=['GET', 'POST'])
def add_destination():
    """Handles adding a new address"""

    error = None

    form = AddDestinationForm()

    if not g.user:
        error = 'Unauthorized access'
        return redirect('/user')

    if form.validate_on_submit():
        new_destination = form.destination.data
        top_price = form.top_price.data
        g.user.base_city = form.base_city.data

        print(f"new_destination: {new_destination}")
        print(f"top_price: {top_price}")
        print(f"g.user.base_city: {g.user.base_city}")


        #Using FlightSearch class to get the destination code
        flight_search = FlightSearch()
        iata_code = flight_search.iata_code(new_destination)

        if iata_code:
            #use the FlightSearch class to check for flights
            from_time = datetime.now() + timedelta(days=1)
            to_time = from_time + timedelta(days=7) #Adjust days is needed

            flight_data = flight_search.check_flights(
                base_city = g.user.base_city,
                iata_code = iata_code,
                from_time = from_time,
                to_time = to_time
            )
            print(f'Destination created: {new_destination}')

            if flight_data:
                try:
                    # Save the destination and flight data to the database
                    new_destination = Destination(
                        destination=new_destination,
                        iata_code=iata_code,
                        top_price=top_price,
                        user=g.user
                    )

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

                    flash('Destination added!')
                    return redirect('/user')  # Redirect to the user homepage after adding destination

                except Exception as e:
                    print(f"Error during database commit: {e}")
                    db.session.rollback()  # Rollback changes in case of an IntegrityError
                    error = 'Error during databse commit'
                    


    error = 'Invalid form submission'
    return render_template('add_destination.html', form=form, user_destinations=g.user.destinations, error=error)

@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    """Update user profile"""

    form = EditUserForm(obj=g.user)

    error = None

    if not g.user:
        error = 'Access unauthorized'
        return redirect('/user')

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.username = form.username.data
            g.user.password = form.password.data
            g.user.address = form.address.data

            db.session.commit()
            return redirect('/user')

        else:
            error = 'Incorrect password'

    return render_template('edit_user.html', form=form, error=error)

@app.route('/delete', methods=['POST'])
def delete_user():
    """Deletes the user"""
    error = None

    if not g.user:
        error = 'Unauthorized access'
        return redirect('/')

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect('/register', error=error)

@app.route('/delete_destination/<int:destination_id>', methods=['POST'])
def delete_destination(destination_id):
    """Allows a user to delete a destination from their list"""
    
    error = None

    if not g.user:
        error = 'Unauthorized access'
        return redirect('/')

    destination = Destinations.query.get_or_404(destination_id)

    if destination.user_id != g.user.id:
        error = 'Action not authorized'
        return redirect('/user')

    db.session.delete(destination)
    db.session.commit()

    return redirect('/user', error=error)

   