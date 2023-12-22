from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired

class RegForm(FlaskForm):
    """Form for registering users"""
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """Form for users to log in"""

    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class AddDestinationForm(FlaskForm):
    """Form for user to add additional addresses once logged in"""
    base_city = StringField('From', validators=[InputRequired()])
    destination = StringField('Destination', validators=[InputRequired()])
    top_price = IntegerField('Top Price', validators=[InputRequired()])
    submit = SubmitField('Add')

class EditProfileForm(FlaskForm):
    """Form user can edit profile"""
    username = StringField('Update username', validators=[InputRequired()])
    password = PasswordField('Update password', validators=[InputRequired()])
    submit = SubmitField('Edit')