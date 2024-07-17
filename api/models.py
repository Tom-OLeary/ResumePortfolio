import os
import time
import pandas as pd

from dataclasses import dataclass, field

from django.conf import settings
from django.db import models


@dataclass
class TeamRecord:
    name: str
    prefix_1: str
    prefix_2: str

    city: str = field(init=False)

    def __post_init__(self):
        _team_city = self.name.split(" ")
        if "Portland" in self.name:
            self.city, *self.name = _team_city
        else:
            *self.city, self.name = _team_city

        self.prefix_1 = self.prefix_1.upper()
        if isinstance(self.city, list):
            self.city = " ".join(self.city)

        if isinstance(self.name, list):
            self.name = " ".join(self.name)

    @property
    def data(self):
        return {
            "city": self.city,
            "name": self.name,
            "abbreviation": self.prefix_1,
            "full_name": self.prefix_2,
        }


class TeamModelManager(models.Manager):
    def load_teams_csv(self, path: str = None):
        # TODO log instead of print
        print(f"Starting team csv import")
        path = path or "api/nba/csv_data/teams.csv"
        before_time = time.time()
        teams_data = pd.read_csv(os.path.join(settings.BASE_DIR, path)).to_dict("records")

        teams = []
        for t in teams_data:
            try:
                team = TeamRecord(**t)
            except TypeError as e:
                print(f"Data Error for team data {t}", e)
                continue

            teams.append(self.model(**team.data))

        self.bulk_create(teams, ignore_conflicts=True)
        after_time = time.time()
        print(f"Finished Creating {len(teams)} team records in {after_time - before_time} seconds")


class Team(models.Model):
    class Meta:
        db_table = "teams"
        unique_together = (("name", "city"),)

    city = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)
    full_name = models.CharField(max_length=100)
    championships = models.IntegerField(default=0)

    objects = TeamModelManager()

    def __str__(self):
        return self.name

    @property
    def active_players(self):
        return self.players.filter(is_active=True)


class PlayerModelManager(models.Manager):
    pass


class Player(models.Model):
    class Meta:
        db_table = "players"

    latest_team = models.ForeignKey(Team, related_name='players', on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    player_id = models.CharField(unique=True)
    is_active = models.BooleanField(default=False)

    objects = PlayerModelManager()




