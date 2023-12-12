import os

from flask import Flask, render_template, redirect, url_for, session, flash, g
from forms import LoginForm, RegForm, AddAddressForm, EditUserForm
from main import find_coords, is_iss_overhead
from models import db, connect_db, bcrypt, Register, User, Coordinates
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, template_folder='templates')
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql:///lookup')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "shhhdonttell")

#this is not in app.py in the twitter clone example
bcrypt.init_app(app) 

connect_db(app)

with app.app_context():
    db.drop_all()

with app.app_context():
    db.create_all()

CURR_USER_KEY = 'user_id'
#CURR_USER_KEY = 'curr_user'

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
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Shows form for user to register, handles submission, adds info to database and redirect to login. If the form is not valid, present form.  If username already exists, flash message and re-present form"""
    
    global MY_LAT, MY_LON

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = RegForm()
       
    if form.validate_on_submit():
        print('Form is valid')

        try:
            print('Before adding user to db')

            user = Register.register(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                address = form.username.data,
                username = form.username.data,
                password = form.password.data,                
            ) 

            print('User:', user)
            db.session.add(user)
            db.session.commit()
        
            flash('Success! Please log in.')

            print('Before redirect to login')
            do_login(user)

            find_coords(form.address.data, user)

            return redirect('/user')
    
        except IntegrityError as e:
            flash(f'Username taken, please try another')

            print('Retrun the registration form on IntegrityError')
            return render_template('register.html', form=form)

    else:
        print(form.errors)
        return render_template('register.html', form=form)
      
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles login"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        
        if user:
            do_login(user)
            return redirect('/user')
        else:
            flash(f'Invalid username/password. Please try again.')
            print(form.errors)
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Handles user logout"""

    do_logout()

    flash(f'Logout successful')
    return redirect('/login')

@app.route('/user', methods=['GET', 'POST'])
def user_homepage():
    """Shows user list of addresses and buttons to complete other tasks"""

    if not g.user:
        flash(f'Unauthorized Access')
        return redirect('/')

    else:
        user_addresses = Coordinates.query.filter_by(user_id=g.user.id).all()

    form = AddAddressForm()

    
    return render_template('user.html', form=form, user_addresses=user_addresses)

@app.route('/add_address', methods=['GET', 'POST'])
def add_address():
    """Handles adding a new address"""

    global MY_LAT, MY_LON

    form = AddAddressForm()

    if not g.user:
        flash('Unauthorized access')
        return redirect('/user')

    if form.validate_on_submit():
        new_address = form.address.data
        
        find_coords(form.address.data, g.user)

        flash('Address added successfully!')
        return redirect('/user')

    flash('Invalid form submission')
    return render_template('add_address.html', form=form, user_addresses=g.user.coordinates)

@app.route('/edit', methods=['GET', 'POST'])
def edit_user():
    """Update user profile"""

    form = EditUserForm(obj=g.user)

    if not g.user:
        flash('Access unauthorsized')
        return redirect('/user')

    # user = g.user

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.username = form.username.data
            g.user.password = form.password.data
            g.user.address = form.address.data

            db.session.commit()
            return redirect('/user')

        else:
            flash(f'Incorrect password')

    return render_template('edit_user.html', form=form)

@app.route('/delete', methods=['POST'])
def delete_user():
    """Deletes the user"""

    if not g.user:
        flash('Unauthorized access')
        return redirect('/')

    db.session.delete(g.user)
    db.session.commit()

    do_logout()
    return redirect('/register')

@app.route('/addresses/delete')
def delete_address():
    """Allows a user to delete an address from their list"""


@app.route('/location', methods=['GET', 'POST'])
def go_outside():
    """pull coordinates from db and check if user should go outside and look up"""

    if not g.user:
        flash('Unauthorized access')
        return redirect('/user')

    user_addresses = Coordinates.query.filter_by(user_id=g.user.id).all()

    for address in user_addresses:
        lat = address.latitude
        lon = address.longitude
    
    response = is_iss_overhead(lat, lon)

    message = 'Go outside and look UP!'
    if response != True:
        message = 'Stay inside'

    return render_template('lookup.html', message=message)