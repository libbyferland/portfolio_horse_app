from flask import Blueprint, request, render_template, flash, url_for, redirect, session
from sqlalchemy import select, exc
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, current_user, logout_user
from . import db
from .models import User
from .dbarn_forms import LogInForm, RegisterForm

bp = Blueprint("auth", __name__, url_prefix = "/auth")

@bp.route("/login", methods = ("GET", "POST"))
def user_login() -> str:
  '''
  Handles log in workflow, including authentication.
  '''
  login_form = LogInForm()
  username = None
  password = None

  if login_form.validate_on_submit():
    username = login_form.username.data
    password = login_form.password.data
    login_form.username.data = ""
    login_form.password.data= ""
  
    error = None
    if username and password:
      entry = db.session.execute(db.select(User).filter_by(name = username)) \
          .scalars().first()
      if entry:
        if check_password_hash(entry.password, password):
          login_user(entry, remember = True)
          if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        else:
          error = f'Incorrect password.  Please try again.'
          flash(error, "error")
      else:
        error = f'User {username} does not exist.  Please try again.'
        flash(error, "error")
  return render_template("auth/login.html", username = username, \
    password = password, form = login_form)

@bp.route("/register", methods = ("GET", "POST"))
def user_register() -> str:
  '''
  Handles registration workflow.  Redirects to log in if registering a 
  new user in the database was successful.
  '''
  register_form = RegisterForm()
  username = None
  password = None

  if register_form.validate_on_submit():
    username = register_form.username.data
    password = register_form.password.data
    register_form.username.data = ""
    register_form.password.data = ""

    error = None
    if username and password:
      current_login = User(name = username, password = generate_password_hash(password))
      try:
        db.session.add(current_login)
        db.session.commit()
      except exc.IntegrityError:
        error = f'User {username} already exists, please create a new username.'
        db.session.rollback()
        flash(error, "error")
        return redirect(url_for("auth.user_register"))

      flash(f'Successfully created user {username}!', 'success')
      return redirect(url_for("auth.user_login"))


  return render_template("auth/register.html", username = username, \
    password = password, form = register_form)

@bp.route("/logout", methods = ("GET", "POST"))
def user_logout():
  '''
  Ends user session.
  '''
  logout_user()
  return redirect(url_for("auth.user_login"))



