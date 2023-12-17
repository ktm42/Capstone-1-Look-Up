from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import InputRequired

class RegForm(FlaskForm):
    """Form for registering users"""
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    address = TextAreaField('Street Address', validators=[InputRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """Form for users to log in"""

    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class AddAddressForm(FlaskForm):
    """Form for user to add additional addresses once logged in"""
    address = TextAreaField('Street Address', validators=[InputRequired()])
    submit = SubmitField('Add')

class EditUserForm(FlaskForm):
    """Form user can edit profile"""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    address = TextAreaField('Street Address', validators=[InputRequired()])
    submit = SubmitField('Edit')



