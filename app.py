import os

from flask import Flask, render_template, redirect, session, flash
from forms import LoginForm, RegForm
#from models import db, connect_db, Register, User, Coordinates
#from sqlalchemy.exe import IntegrityError

app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///lookup'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

#connect_db(app)

# @app.before_request
# def add_user_to_g():

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None

# def do_login(user):
#     """Log in user"""

#     session[CURR_USER_KEY] = user.id 

# def do_logout():
#     """Logs out user"""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Shows form for user to register and handles submission"""

    form = RegForm()
       
    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                password = form.password.data,                
            ) 
        
            db.session.commit()
    
        except IntegrityError as e:
            flash(f'Username already exists')
            return render_template('register.html', form=form)

        do_login(user)

        return redirect('/')
    else:
        return render_template('register.html', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles login"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        
        if user:
            do_login(user)
            flash(f'Hi {user.username}!')
            return redirect('/')
        else:
            flash(f'Invalid username/password. Please try again.')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Handels user logout"""

    do_logout()

    flash(f'Logout successful')
    return redirect('/login')

#@app.route('/location') #need a way to delete out or edit a location and also a way to delete the user completely