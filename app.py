import os

from flask import Flask, render_template, redirect, url_for, session, flash, g
from forms import LoginForm, RegForm
from main import find_coords, is_iss_overhead, is_night
from models import db, bcrypt, Register, User, Coordinates
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, template_folder='templates')
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql:///lookup')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "shhhdonttell")

db.init_app(app)
bcrypt.init_app(app)

from models import connect_db

connect_db(app)

with app.app_context():
    db.drop_all()

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
         
            return redirect('/login')
    
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Error: {e}')

            print('Retrun the registration form on IntegrityError')
            return render_template('register.html', form=form)

    else:
        print('Form is invalid')
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
            flash(f'Hi {user.username}, welcome back!')
            return redirect('/')
        else:
            flash(f'Invalid username/password. Please try again.')
            print(form.errors)
    
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    """Handles user logout"""

    do_logout()

    flash(f'Logout successful')
    return redirect('/login')


@app.route('/delete', methods=['POST'])
def delete_user():
    """Deletes the user"""

    if not g.user:
        flash('Unauthorized access')
        return redirect('/')

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect('/register')



@app.route('/location', methods=['GET', 'POST'])
def go_outside():
    """pull coordinates from db and check if user should go outside and look up"""

    is_iss_overhead()
    is_night()