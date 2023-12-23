import os

from flask import Flask, render_template, redirect, url_for, session, request, flash, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from forms import LoginForm, RegForm, AddDestinationForm, EditProfileForm
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
    
    return render_template('user.html', user_destinations=user_destinations, error=error)

@app.route('/add_destination', methods=['GET', 'POST'])
def add_destination():
    """Handles adding a new destination"""
    
    error = None

    if not g.user:
        error = 'Unauthorized access'
        return redirect('/user')

    form = AddDestinationForm()    

    if request.method == 'POST' and form.validate_on_submit():
        new_destination = form.destination.data
        top_price = form.top_price.data
        g.user.base_city = form.base_city.data

        # Using FlightSearch class to get the destination code
        flight_search = FlightSearch()
        iata_code = flight_search.iata_code(new_destination)

        if iata_code:
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
                flash('Destination added!')
                return redirect('/user')  # Redirect to the user homepage after adding destination

            except Exception as e:
                print(f"Error during database commit: {e}")
                db.session.rollback()  # Rollback changes in case of an IntegrityError
                error = 'Error during database commit'

        else:
            print(f"Form errors: {form.errors}")
            print(f"CSRF Token: {form.csrf_token.data}")
            error = 'Invalid form submission'

    return render_template('add_destination.html', form=form, user_destinations=g.user.destinations, error=error)

@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    """Update user profile"""

    form = EditProfileForm(obj=g.user)

    error = None

    if not g.user:
        error = 'Access unauthorized'
        return redirect('/user')

    if form.validate_on_submit():
            g.user.username = form.username.data
            g.user.password = form.password.data
        
            db.session.commit()
            return redirect('/user')
        
    return render_template('edit_profile.html', form=form, error=error)

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

    flash('Successfully deleted')
    return redirect('/register')

@app.route('/delete_destination/<int:destination_id>', methods=['POST'])
def delete_destination(destination_id):
    """Allows a user to delete a destination from their list"""
    
    error = None

    if not g.user:
        error = 'Unauthorized access'
        return redirect('/')

    destination = Destination.query.get_or_404(destination_id)

    if destination.user_id != g.user.id:
        error = 'Action not authorized'
        return redirect('/user')

    db.session.delete(destination)
    db.session.commit()

    return redirect('/user')

   