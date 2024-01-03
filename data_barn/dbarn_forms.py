from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class LogInForm(FlaskForm):
  '''
  Basic log in form elements - text entry for user name and password and 
  submit button.  Subclasses FlaskForm base class from flask_wtf
  '''
  username = StringField("Username", \
      validators=[DataRequired("Please enter a user name")])
  password = PasswordField("Password", \
      validators=[DataRequired("Password required")])
  login = SubmitField("Log in")

class RegisterForm(LogInForm):
  '''
  Form elements for user registration form.  Changes submit button
  from LogInForm class to read "Register"
  '''
  login = SubmitField("Register")

