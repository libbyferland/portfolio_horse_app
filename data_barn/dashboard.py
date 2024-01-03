from flask import Blueprint, request, render_template, flash, url_for, redirect, session
from sqlalchemy import select, exc, func
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, current_user
from . import db
from .models import Entry, Horse, Jockey, Trainer
from .db_handler import DBHandler

bp = Blueprint("dashboard", __name__, url_prefix = "/")
dbh = DBHandler()

@bp.route("/", methods = ("GET", "POST"))
@login_required
def dashboard() -> str:
  '''
  Displays main page of app.  View requires authenticated user.
  '''
  return render_template("main/index.html")

@bp.route("/aggregates/<measure>", methods = ("GET",))
@login_required
def aggregator(measure = None) -> str:
  '''
  Takes measure passed in from index page (sires, jockeys, trainers) and 
  queries database to create aggregate data (ex. wins in turf races).
  View requires authenticated user.
  '''
  if request.method == "GET":
    if measure == "sires":
      sires = dbh.all_aggregate_wins(Horse)
      return render_template("main/sires.html", sires = sires, measure = "sires")
    if measure == "jockeys":
      jockeys = dbh.all_aggregate_wins(Jockey)
      return render_template("main/jockeys.html", jockeys = jockeys, measure = "jockeys")
    if measure == "trainers":
      trainers = dbh.all_aggregate_wins(Trainer)
      return render_template("main/trainers.html", trainers = trainers, measure = "trainers")

  return render_template("main/index.html")


