import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Date 
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
  '''
  Implements user table from thoroughbred_api database.  Subclasses UserMixin
  from flask_login to handle user authentication using ORM.
  '''
  __tablename__ = "user"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  name = db.Column(String(15), nullable = False, unique = True)
  password = db.Column(String(256), nullable = False)
  perms = db.Column(String(15), nullable = False, default = "guest")

  def is_authenticated(self) -> bool:
    '''
    Required by flask_login.  Should be inverse of is_anonymous().
    '''
    return True

  def is_active(self) -> bool:
    '''
    Required by flask_login.
    '''
    return True

  def is_anonymous(self) -> bool:
    '''
    Required by flask_login.  Should be inverse of is_authenticated().
    '''
    return False
  
  def get_id(self) -> str:
    '''
    Required by flask_login.  Return type must be string per API docs.
    Return:
      str: UUID PK from user table as string
    '''
    return self.id.hex

  def __repr__(self) -> str:
    return f'User(name = {self.name})'


class Horse(db.Model):
  '''
  Implements horse table from thoroughbred_api database.
  '''
  __tablename__ = "horse"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  name = db.Column(String(30), nullable = False)
  sire_id = db.Column(UUID(as_uuid = True), ForeignKey("horse.id"))
  owner_id = db.Column(UUID(as_uuid = True), ForeignKey("owner.id"))
  trainer_id = db.Column(UUID(as_uuid = True), ForeignKey("trainer.id"))

  owner = relationship("Owner", back_populates = "stable")
  trainer = relationship("Trainer", back_populates = "clients")
  won = relationship("Running", back_populates = "winner", uselist = True)
  entered = relationship("Entry", back_populates = "horse", uselist = True)

 
  def __repr__(self) -> str:
    return f'Horse(name={self.name})'


class Track(db.Model):
  '''
  Implements track table from thoroughbred_api database.
  '''
  __tablename__ = "track"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  abbreviation = db.Column(String(5), nullable = False)
  name = db.Column(String(50))
  location = db.Column(String(60))

  def __repr__(self) -> str:
    return f'Track(abbreviation = {self.abbreviation})'


class Race(db.Model):
  '''
  Implements race table from thoroughbred_api database.
  '''
  __tablename__ = "race"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  track_id = db.Column(UUID(as_uuid = True), ForeignKey("track.id"))
  type = db.Column(String(15), nullable = False)
  restriction = db.Column(String(15), nullable = False, default = "open")
  distance = db.Column(Float(3), nullable = False)
  surface = db.Column(String(10), nullable = False)
  name = db.Column(String(50))
  grade = db.Column(Integer)

  was_run = relationship("Running", back_populates = "race", uselist = True) 

  def __repr__(self) -> str:
    return f'Race(distance = {self.distance}, type = {self.type})'


class Running(db.Model):
  '''
  Implements running table from thoroughbred_api database.  Each entry
  in the table is a specific instance of a type of race (eg., the 2013 running
  of the Blue Grass Stakes).
  '''
  __tablename__ = "running"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  race_id = db.Column(UUID(as_uuid = True), ForeignKey("race.id"), \
      nullable = False)
  meet = db.Column(String(15))
  date = db.Column(Date, nullable = False)
  num_on_day = db.Column(Integer)
  field_size = db.Column(Integer)
  off_track = db.Column(Boolean, nullable = False, default = False)
  winner_id = db.Column(UUID(as_uuid = True), ForeignKey("horse.id"))
  winning_post = db.Column(Integer)
  half_mile_seconds = db.Column(Float(6))
  final_seconds = db.Column(Float(6))
  half_mile_winner_position = db.Column(Float(4))

  race = relationship("Race", back_populates = "was_run")
  winner = relationship("Horse", back_populates = "won")
  field = relationship("Entry", back_populates = "entered", uselist = True)

  def __repr__(self) -> str:
    return f'Running(race_id = {self.race_id}, date = {self.date})'


class Entry(db.Model):
  '''
  Implements entry table from thoroughbred_api database.  Each record in the
  table corresponds to an individual horse running in a specific race,
  analogous to past performances.
  '''
  __tablename__ = "entry"

  horse_id = db.Column(UUID(as_uuid = True), ForeignKey("horse.id"), \
      primary_key = True)
  running_id = db.Column(UUID(as_uuid = True), ForeignKey("running.id"), \
      primary_key = True)
  jockey_id = db.Column(UUID(as_uuid = True), ForeignKey("jockey.id"))
  owner_id = db.Column(UUID(as_uuid = True), ForeignKey("owner.id"))
  trainer_id = db.Column(UUID(as_uuid = True), ForeignKey("trainer.id"))
  post_position = db.Column(Integer)
  odds = db.Column(Float(4))
  scratch = db.Column(Boolean, default = False)
  past_turf_starts = db.Column(Integer)
  past_turf_wins = db.Column(Integer)
  past_polytrack_starts = db.Column(Integer)
  past_polytrack_wins = db.Column(Integer)
  last_raced = db.Column(Date)
  last_raced_track_id = db.Column(UUID(as_uuid = True), ForeignKey("track.id"))
  last_raced_distance = db.Column(Float(3))
  last_raced_surface = db.Column(String(15))
  last_workout_track_id = db.Column(UUID(as_uuid = True), \
      ForeignKey("track.id"))
  
  horse = relationship("Horse", back_populates = "entered")
  entered = relationship("Running", back_populates = "field")
  jockey = relationship("Jockey", back_populates = "rode_in")
  owner = relationship("Owner")
  trainer = relationship("Trainer")
  last_raced_at = relationship("Track", \
      primaryjoin = last_raced_track_id == Track.id, post_update = True)
  last_workout_at = relationship("Track",\
      primaryjoin = last_workout_track_id == Track.id, \
      post_update = True)

  def __repr__(self) -> str:
    return f'Entry(horse_id = {self.horse_id}, post_position = ' + \
        f'{self.post_position}, odds = {self.odds})'



class Owner(db.Model):
  '''
  Implements owner table from thoroughbred_api database.  Does not split owner
  names because multiple owners and entities can exist per horse.
  '''
  __tablename__ = "owner"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  name = db.Column(String(256))

  stable = relationship("Horse", back_populates = "owner", uselist = True)

  def __repr__(self) -> str:
    return f'Owner(name = {self.name})'


class Trainer(db.Model):
  '''
  Implements trainer table from thoroughbred_api database.
  '''
  __tablename__ = "trainer"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  first_name = db.Column(String(20))
  last_name = db.Column(String(30))

  clients = relationship("Horse", back_populates = "trainer", uselist = True)

  def __repr__(self) -> str:
    return f'Trainer(last_name = {self.last_name}, ' + \
        f'first_name = {self.first_name})'


class Jockey(db.Model):
  '''
  Implements jockey table from thoroughbred_api database.
  '''
  __tablename__ = "jockey"

  id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
  first_name = db.Column(String(20))
  last_name = db.Column(String(30))

  rode_in = relationship("Entry", back_populates = "jockey", uselist = True)

  def __repr__(self) -> str:
    return f'Jockey(last_name = {self.last_name}, ' + \
        f'first_name = {self.first_name})'



