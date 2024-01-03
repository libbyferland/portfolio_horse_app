import csv
from sqlalchemy import exc
from data_barn import db, models
from datetime import date
import uuid

class DataLoader(object):
  '''
  Helper class to load data from CSV file formatted in the style of the
  Keeneland data into a database.

  Attributes:
    entries: list[dict[str, str]]
      An individual row in the CSV file containing information to be
      inserted into the database

    track: UUID
      The database id for Keeneland.  Attribute specific to the dataset in
      "keeneland.csv"

  Methods:
    __init__(csv_file):
      Takes name of CSV file as string and loads each row as a dict with
      CSV headers as keys.  Stores list of dict objects in the self.entries
      attribute.

    insert_*(row):
      Where * is the lowercase name of a table in the thoroughbred_api 
      database.  Extracts relevant information from a dict item in
      self.entries and creates necessary database records.

    batch_process():
      Creates records for all dict items in self.entries

    _clean_name(person):
      Takes a person's names and splits it into first and last name for 
      database record (relevant to trainer and jockey).



  '''
  def __init__(self, csv_file: str = "") -> None:
    '''
    Constructor for DataLoader.  Does the initial processing of CSV file
    and stores each row in a dict to be used to create records in the 
    thoroughbred_api database.  Cleans people names to get first, last.  Also
    sets track to Keeneland since data is currently only relevant to Keeneland.
    This is done as a small optimization in time since the PK for track is 
    used in another table.

    Parameters:
    csv_file: str
      Name of CSV file containing dataset.
    '''
    self.entries = []
    if csv_file:
      with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          self.entries.append(row)
    if self.entries:
      for e in self.entries:
        jockey = e["WinnersJockey"]
        trainer = e["WinnersTrainer"]
        e["WinnersOwner"].strip()
        e["WinnersJockey"] = self._clean_name(jockey)
        e["WinnersTrainer"] = self._clean_name(trainer)
        self.track = db.session.execute(db.select(models.Track) \
            .filter_by(abbreviation = "KEE")).fetchone()[0].id


  def insert_horse(self, row: dict[str, str]) -> dict[str, uuid.UUID]:
    '''
    Given a dict from a row in the CSV file, inserts relevant records into 
    horse table.  Horse requires UUIDs for trainers, owners, and sires so
    those records are also created if they do not exist.  Pulls out and returns
    these three UUIDs since they're used to connect several tables.

    Parameters:
      row: dict[str, str]
        Row from CSV file

    Returns: dict[str, uuid.UUID]
      UUIDs for horse, trainer, and owner -- these link the horse table, 
      running table, and entry table.
    '''
    hname = row["HorseName"]
    sire = row["WinnersSire"]
    owner = row["WinnersOwner"]
    trainer = row["WinnersTrainer"]
    
    sire_exists = db.session.execute(db.select(models.Horse) \
        .filter_by(name = sire)).fetchone()
    if sire_exists:
      sire_id = sire_exists[0].id
    else:
      sire_entry = models.Horse(name = sire)
      db.session.add(sire_entry)
      db.session.commit()
      sire_id = sire_entry.id

    trainer_select = db.select(models.Trainer) \
        .filter(models.Trainer.last_name == trainer["last_name"], \
        models.Trainer.first_name == trainer["first_name"])

    trainer_exists = db.session.execute(trainer_select).fetchone()
    if trainer_exists:
      trainer_id = trainer_exists[0].id

    else:
      trainer_entry = models.Trainer(last_name = trainer["last_name"], \
          first_name = trainer["first_name"])
      db.session.add(trainer_entry)
      db.session.commit()
      trainer_id = trainer_entry.id

    owner_exists = db.session.execute(db.select(models.Owner) \
        .filter_by(name = owner)).fetchone()
    if owner_exists:
      owner_id = owner_exists[0].id
    else:
      owner_entry = models.Owner(name = owner)
      db.session.add(owner_entry)
      db.session.commit()
      owner_id = owner_entry.id

    horse_select = db.select(models.Horse).filter(models.Horse.name == hname, \
                  models.Horse.owner_id == owner_id, \
                  models.Horse.trainer_id == trainer_id, \
                  models.Horse.sire_id == sire_id)

    exists = db.session.execute(horse_select).fetchone()
    if exists:
      return {"horse": exists[0].id, "owner": owner_id, "trainer": trainer_id}

    this_horse = models.Horse(name = hname, owner_id = owner_id, \
        trainer_id = trainer_id, \
        sire_id = sire_id)

    db.session.add(this_horse)
    db.session.commit()

    return {"horse": this_horse.id, "owner": owner_id, "trainer": trainer_id}

  def insert_race(self, row: dict[str, str]) -> uuid.UUID:
    '''
    Inserts race record into table using relevant items from row in CSV file.
    This is then associated with a running record, or a specific instance of
    a race being run.  Returns PK for record to be used in other tables.

    Parameters:
      row: dict[str, str]
        A row from the CSV file loaded into self.entries

    Returns: uuid.UUID
      The PK for the record inserted into the race table
    '''
    race_type = row["RaceType"]
    extended = row["ExtendedRaceType"]
    surface = row["Surface"].strip()
    distance = float(row["Distance"])
    grade = 0
   

    if race_type == "STK":
      if extended[1].isdigit():
        grade = int(extended[1])
        name = extended[2:]
        nameish = f'%{name.split()[0]}%'
      else:
        nameish = f'%{extended.split()[0]}%'
        name = extended
        grade = 4
      race_select = db.select(models.Race).filter(models.Race.type == race_type, \
          models.Race.name.like(nameish), models.Race.distance == distance, \
          models.Race.grade == grade, \
          models.Race.surface == surface, models.Race.track_id == self.track)
    else:
      race_select = db.select(models.Race).filter(models.Race.type == race_type, \
          models.Race.restriction == extended, models.Race.distance == distance, \
          models.Race.surface == surface, models.Race.track_id == self.track)
    
    entry = db.session.execute(race_select).fetchone()

    if entry:
      return entry[0].id
    else:
      if race_type == "STK":
        race = models.Race(type = "STK", name = name, grade = grade, \
            distance = distance, \
            surface = surface, track_id = self.track)
      else:
        race = models.Race(type = race_type, restriction = extended, \
            distance = distance, \
            surface = surface, track_id = self.track)

      db.session.add(race)
      db.session.commit()
      
      return race.id


  def insert_running(self, row: dict[str, str]) -> tuple[uuid.UUID, \
      dict[str, uuid.UUID]]:
    '''
    Inserts a running record into the table, representing a specific dated
    instance of a race.  Inserts a race record if none exists and inserts
    a horse if no entry exists for the winning horse.

    Parameters:
      row: dict[str, str]
        A dict object read in from CSV file.

    Returns: tuple[uuid.UUID, dict[str, uuid.UUID]]
      The PK for the running record that was inserted as well as the UUID
      dict from the insert_horse() function containing UUIDs for horse,
      trainer, and owner of the winner
    '''
    meet = row["RaceMeet"]
    card_num = int(row["RaceNumber"])
    field = int(row["FieldSize"])
    race = self.insert_race(row)
    winner_stats = self.insert_horse(row)
    winner = winner_stats["horse"]
    half_mile = float(row["HalfMileTime"])
    final = float(row["FinalTime"])
    half_winner = float(row["HalfMilePosition"])
    ran_on = row["RaceDate"].split("/")
    ran_date = date(int(ran_on[2]), int(ran_on[0]), int(ran_on[1]))
    win_post = int(row["WinningPostPosition"])
    run = models.Running(race_id = race, date = ran_date, \
        half_mile_seconds = half_mile, \
        final_seconds = final, half_mile_winner_position = half_winner, \
        winner_id = winner, \
        num_on_day = card_num, field_size = field, meet = meet, \
        winning_post = win_post)
    db.session.add(run)
    db.session.commit()

    return run.id, winner_stats

  def insert_jockey(self, row: dict[str, str]) -> uuid.UUID:
    '''
    Inserts record into jockey table if none exists or returns existing entry.
    Jockey is in a 1:many relationship with the entry table.

    Parameters:
      row: dict[str, str]
        Dict object from self.entries, read in from CSV file

    Returns: uuid.UUID
      The PK for the jockey record.

    '''
    jockey = row["WinnersJockey"]
    exists = db.session.execute(db.select(models.Jockey) \
        .filter(models.Jockey.first_name == jockey["first_name"], \
        models.Jockey.last_name == jockey["last_name"])).fetchone()

    if exists:
      return exists[0].id

    j = models.Jockey(first_name = jockey["first_name"], \
        last_name = jockey["last_name"])
    db.session.add(j)
    db.session.commit()

    return j.id

  def insert_track(self, abbrv: str) -> uuid.UUID:
    '''
    Inserts track into database or returns ID if record exists.  Depends on 
    commonly used track abbreviation.  Also uses self.track for minor 
    optimization since the dataset is tied to Keeneland.

    Parameters:
      abbrv: str
        The commonly used abbreviation for a track.

    Returns: uuid.UUID
      The PK for the record of a track.
    '''
    if abbrv == "KEE":
      return self.track

    exists = db.session.execute(db.select(models.Track) \
        .filter_by(abbreviation = abbrv)).fetchone()

    if exists:
      return exists[0].id
    else:
      new_track = models.Track(abbreviation = abbrv)
      db.session.add(new_track)
      db.session.commit()

      return new_track.id
    

  def insert_entry(self, row: dict[str, str], run: uuid.UUID, \
      winner: dict[str, uuid.UUID]) -> tuple[uuid.UUID, uuid.UUID]:
    '''
    Inserts entry record into database, analogous to past performance
    entry in racing form.  Inserts jockey record into database if none
    exists.  Entry is in a 1:many relationship with a running
    record, although in the current dataset only winners are recorded.

    Parameters:
      row: dict[str, str]
        Dict item from self.entries
      run: uuid.UUID
        PK for corresponding "running" record
      winner: dict[str, uuid.UUID]
        Return from insert_horse function with PKs for winning horse,
        winning trainer, and winning owner

    Returns: tuple[uuid.UUID, uuid.UUID]
      UUIDs for the horse and running, FK pair used as PK in entry
      table.
    '''
    horse = winner["horse"]
    jockey = self.insert_jockey(row)
    owner = winner["owner"]
    trainer = winner["trainer"]
    pp = int(row["WinningPostPosition"])
    odds = float(row["odds"])
    past_t_st = int(row["PriorTurfStarts"])
    past_t_w = int(row["PriorTurfWins"])
    past_p_st = int(row["PriorPolytrackStarts"])
    past_p_w = int(row["PriorPolytrackWins"])
    lr = row["LastRaceDate"].strip()
    if lr:
      lr = lr.split("/")
      last_r_date = date(int(lr[2]), int(lr[0]), int(lr[1]))
    else:
      last_r_date = None
    last_track = self.insert_track(row["LastRaceLocation"])
    last_dist = float(row["LastRaceDistance"])
    last_surf = row["LastRaceSurface"]
    last_workout = self.insert_track(row["LastWorkoutLocation"])

    entry = models.Entry(horse_id = horse, running_id = run, \
        jockey_id = jockey, owner_id = owner, \
        post_position = pp, odds = odds, past_turf_starts = past_t_st, \
        past_turf_wins = past_t_w, \
        past_polytrack_starts = past_p_st, past_polytrack_wins = past_p_w, \
        last_raced = last_r_date, \
        last_raced_track_id = last_track, last_raced_distance = last_dist, \
        last_raced_surface = last_surf, last_workout_track_id = last_workout, \
        trainer_id = trainer)

    db.session.add(entry)
    db.session.commit()

    return horse, run


  def batch_process(self) -> None:
    '''
    Breaks out relevant database records from each row in the CSV for the 
    original dataset (self.entries).  Creates a running record (individual
    instance of a race) and an entry record (past performance).
    '''
    for e in self.entries:
      running_id, winner_info = self.insert_running(e)
      _, _ = self.insert_entry(e, running_id, winner_info)





  def _clean_name(self, person: str) -> dict[str, str]:
    '''
    Takes an unprocessed name string and splits it into first and last.
    Any middle initials or suffixes (eg., Jr.) are currently included in
    first name.

    Parameters:
      person: str
        Unprocessed name from original dataset

    Returns: dict[str, str]
      First and last name split out from original string to be used in
      database record.
    '''
    words = person.split()
    temp = [w for w in words]
    name = {}
    if len(words) < 3:
      name["first_name"] = words[1]
      name["last_name"] = words[0]
    else:
      if words[1] not in ["Jr.", "II", "III", "IV", "V"]:
        name["last_name"] = words[0] + " " + words[1]
        name["first_name"] = words[2]
      else:
        name["first_name"] = words[2] + " " + words[1]
        name["last_name"] = words[0]

    return name


  
