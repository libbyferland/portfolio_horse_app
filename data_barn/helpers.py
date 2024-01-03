import csv
from sqlalchemy import exc
from handycap_genie import db, models

class DataHandler(object):
  def __init__(self, csv_file = ""):
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
        e["WinnersJockey"] = self._clean_name(jockey)
        e["WinnersTrainer"] = self._clean_name(trainer)


  def insert_horse(self, row):
    hname = row["HorseName"]
    sire = row["WinnersSire"]
    owner = row["WinnersOwner"]
    trainer = row["WinnersTrainer"]
   
    sire_exists = db.session.execute(db.select(Horse).filter_by(name = sire)).fetchone()
    if sire_exists:
      sire_id = sire_exists.id
    else:
      sire_entry = models.Horse(name = sire)
      db.session.add(sire_entry)
      db.session.commit()
      sire_id = sire_entry.id

    trainer_select = db.select(Trainer).filter(Trainer.last_name == trainer["last_name"], \
        Trainer.first_name == trainer["first_name"])

    trainer_exists = db.session.execute(trainer_select).fetchone()
    if trainer_exists:
      trainer_id = trainer_exists.id

    else:
      trainer_entry = models.Trainer(last_name = trainer["last_name"], first_name = trainer["first_name"])
      db.session.add(trainer_entry)
      db.session.commit()
      trainer_id = trainer_entry.id

    owner_exists = db.session.execute(db.select(Owner).filter_by(name = owner)).fetchone()
    if owner_exists:
      owner_id = owner_exists.id
    else:
      owner_entry = models.Owner(name = owner)
      db.session.add(owner_entry)
      db.session.commit()
      owner_id = owner_entry.id

    this_horse = models.Horse(name = hname, owner_id = owner_id, trainer_id = trainer_id, \
        sire_id = sire_id)
    db.session.add(this_horse)
    db.session.commit()







  def _clean_name(person):
    words = person.split()
    temp = [w for w in words]
    name = {}
    if len(words) < 3:
      name["first_name"] = words[1]
      name["last_name"] = words[0]
    else:
      if words[1] not in ["Jr.", "II", "III", "IV", "V"]:
        name["last_name"] = words[0] + words[1]
        name["first_name"] = words[2]
      else:
        name["first_name"] = words[2] + words[1]
        name["last_name"] = words[0]

    return name


  
