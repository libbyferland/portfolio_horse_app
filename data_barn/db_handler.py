from sqlalchemy import select, exc, func
#from sqlalchemy.sql import in_
from .models import Jockey, Entry, Horse, Trainer, Running, Race
from . import db, app

class DBHandler(object):
  '''
  Wrapper class for database operations.

  Attributes:
    _total_indexed: int
      Total number of races in database.

  Methods:
    __init__(): 
      Stores total number of races in database as member variable.

    total_indexed():
      Getter for number of races.

    wins_all_time(party):
      Finds total number of wins in database for each sire, jockey, or trainer.

    wins_by_surface_type(party):
      Finds total wins for each sire, jockey, or trainer for polytrack and turf
      races.

    wins_by_race_type(party):
      Finds total wins for each sire, jockey, or trainer for maiden, claiming,
      allowance, and stakes races.

    wins_by_distance(party):
      Finds total wins for each sire, jockey, or trainer for route and sprint
      races.

    all_aggregate_wins(party):
      Combines wins_all_time and wins_by_*.

    _get_aggregate_winners_where_tie(results_list):
      Takes dictionaries from wins_* functions and extracts top three winning
      numbers with any number of associated trainers, jockeys, or sires.

    _get_total_races_indexed():
      Finds total number of races currently recorded in database.
  '''
  def __init__(self):
    with app.app_context():

      self._total_indexed = self._get_total_races_indexed()

  @property
  def total_indexed(self) -> int:
    return self._total_indexed

  def wins_all_time(self, party) -> dict[dict[int, list]]:
    if party == Horse: # Horse stands in for "sires" measures
      stmt = db.select(party.sire_id, func.count(party.sire_id) \
          .label("wins")).join(Entry).group_by(party.sire_id)
      subq = (stmt.cte())
      full_join = db.select(party.name, subq.c.wins).select_from(party) \
          .join(subq, party.id == subq.c.sire_id).order_by(subq.c.wins.desc())
    else:
      stmt = db.select(party.id, func.count(party.id).label("wins")) \
          .join(Entry).group_by(party.id)
      subq = (stmt.cte())
      full_join = db.select(party.first_name, party.last_name, subq.c.wins) \
          .select_from(party).join(subq, party.id == subq.c.id) \
          .order_by(subq.c.wins.desc())

    result = db.session.execute(full_join).fetchall()
    top_three_with_ties = self._get_aggregate_winners_where_tie(result)

    return top_three_with_ties

  def wins_by_surface_type(self, party) -> dict[dict[int, list]]:
    avail_surfaces = ["Turf", "Polytrack"]
    surf_wins = {}
    
    for surface in avail_surfaces:
      if party == Horse:
        sires = db.select(party.sire_id, func.count(party.sire_id).label("wins")) \
            .select_from(party).join(Entry).join(Running).join(Race) \
            .filter_by(surface = surface).group_by(party.sire_id) 
        subq = (sires.cte())
        stmt = db.select(party.name, subq.c.wins).select_from(party) \
            .join(subq, party.id == subq.c.sire_id) \
            .order_by(subq.c.wins.desc())
      else:
        stmt = db.select(party.first_name, party.last_name, \
            func.count(party.id).label("wins")).select_from(party) \
            .join(Entry).join(Running) \
            .join(Race).filter_by(surface = surface).group_by(party.id) \
            .order_by(func.count(party.id).desc())
            
      result = db.session.execute(stmt).fetchall()
      surf_wins[surface] = self._get_aggregate_winners_where_tie(result)

    return surf_wins

  def wins_by_race_type(self, party) -> dict[dict[int, list]]:
    avail_types = {"maiden": ["MSW", "MCL"], "claim": ["MCL", "CLM"], "allowance": ["ALW"], \
        "stakes": ["STK", "STR"]}

    wins_by_type = {}

    for race_type in avail_types:
      if party == Horse:
        sires = db.select(party.sire_id, func.count(party.sire_id) \
            .label("wins")).select_from(party).join(Entry).join(Running) \
            .join(Race).where(Race.type.in_(avail_types[race_type])) \
            .group_by(party.sire_id)
        subq = sires.cte()
        stmt = db.select(party.name, subq.c.wins).select_from(party) \
            .join(subq, party.id == subq.c.sire_id) \
            .order_by(subq.c.wins.desc())
      else:
        stmt = db.select(party.first_name, party.last_name, \
            func.count(party.id).label("wins")).select_from(party) \
            .join(Entry).join(Running).join(Race) \
            .where(Race.type.in_(avail_types[race_type])).group_by(party.id) \
            .order_by(func.count(party.id).desc())

      result = db.session.execute(stmt).fetchall()
      wins_by_type[race_type] = self._get_aggregate_winners_where_tie(result)

    return wins_by_type


  def wins_by_distance(self, party) -> dict[dict[int, list]]:
    wins_by_dist_class = {}
    #by horse racing terms, a sprint is 7 furlongs or less
    #route is somewhat arbitrary, but some international races can be 4 miles+
    distance_cutoffs = {"sprint": Race.distance <= 7, \
        "route": Race.distance > 7}

    for cut in distance_cutoffs:
      if party == Horse:
        sires = db.select(party.sire_id, func.count(party.sire_id) \
            .label("wins")).select_from(party).join(Entry).join(Running) \
            .join(Race).where(distance_cutoffs[cut]) \
            .group_by(party.sire_id)
        subq = sires.cte()
        stmt = db.select(party.name, subq.c.wins).select_from(party) \
            .join(subq, party.id == subq.c.sire_id) \
            .order_by(subq.c.wins.desc())
      else:
        stmt = db.select(party.first_name, party.last_name, \
            func.count(party.id).label("wins")).select_from(party) \
            .join(Entry).join(Running).join(Race) \
            .where(distance_cutoffs[cut]).group_by(party.id) \
            .order_by(func.count(party.id).desc())

      result = db.session.execute(stmt).fetchall()
      wins_by_dist_class[cut] = self._get_aggregate_winners_where_tie(result)

    return wins_by_dist_class

  def all_aggregate_wins(self, party) -> dict:
    wins_by_stat_type = {}

    wins_by_stat_type["all_time"] = self.wins_all_time(party)
    wins_by_stat_type["surface"] = self.wins_by_surface_type(party)
    wins_by_stat_type["race_type"] = self.wins_by_race_type(party)
    wins_by_stat_type["distance"] = self.wins_by_distance(party)

    return wins_by_stat_type

  def _get_aggregate_winners_where_tie(self, results_lst):
    wins_with_ties = {}
    top_three_wins = []
    top = results_lst[0].wins
    temp_results = results_lst[:]
    while len(wins_with_ties) < 3:
      wins_with_ties[top] = []
      cutoff = sum(1 for sire in temp_results if sire.wins == top)
      wins_with_ties[top] += temp_results[:cutoff]
      temp_results = temp_results[cutoff:]
      top = temp_results[0].wins

    return wins_with_ties


  def _get_total_races_indexed(self) -> int:
    stmt = db.select(func.count(Running.id)).select_from(Running)
    result = db.session.execute(stmt).scalar()

    return result




