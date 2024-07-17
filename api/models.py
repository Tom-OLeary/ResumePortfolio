import json
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

    @property
    def inactive_players(self):
        return self.players.filter(is_active=False)

    @property
    def all_players(self):
        return self.players.all()


@dataclass
class PlayerRecord:
    PERSON_ID: str
    PLAYER_LAST_NAME: str
    PLAYER_FIRST_NAME: str
    TEAM_CITY: str
    TEAM_NAME: str
    TEAM_ABBREVIATION: str
    JERSEY_NUMBER: int
    POSITION: str
    HEIGHT: str
    WEIGHT: float
    COLLEGE: str
    COUNTRY: str
    DRAFT_YEAR: str
    DRAFT_ROUND: str
    DRAFT_NUMBER: str
    ROSTER_STATUS: str
    PTS: float
    REB: float
    AST: float
    TO_YEAR: str

    def __post_init__(self):
        self.latest_team = Team.objects.filter(abbreviation=self.TEAM_ABBREVIATION).first()

    @property
    def data(self):
        return {
            "latest_team": self.latest_team,
            "first_name": self.PLAYER_FIRST_NAME,
            "last_name": self.PLAYER_LAST_NAME,
            "player_id": self.PERSON_ID,
            "height": self.HEIGHT,
            "weight": self.WEIGHT,
            "position": self.POSITION,
            "jersey_number": self.JERSEY_NUMBER,
            "draft_pick": self.DRAFT_NUMBER,
            "draft_year": self.DRAFT_YEAR,
            "draft_round": self.DRAFT_ROUND,
            "final_year": self.TO_YEAR,
            "college": self.COLLEGE,
            "country": self.COUNTRY,
            "is_active": self.ROSTER_STATUS,
            "career_pts_avg": self.PTS,
            "career_reb_avg": self.REB,
            "career_ast_avg": self.AST,
        }


class PlayerModelManager(models.Manager):
    IGNORE_FIELDS = [
        "Unnamed: 0",
        "PLAYER_SLUG",
        "TEAM_ID",
        "TEAM_SLUG",
        "IS_DEFUNCT",
        "STATS_TIMEFRAME",
        "FROM_YEAR",
    ]

    def load_players_csv(self, path: str = None):
        path = path or "api/nba/csv_data/player_index.csv"
        player_data = pd.read_csv(os.path.join(settings.BASE_DIR, path)).to_dict("records")

        players = []
        for row in player_data:
            try:
                player = PlayerRecord(**{k: v for k, v in row.items() if k not in self.IGNORE_FIELDS})
            except TypeError as e:
                print(f"Data Error for player data {row}", e)
                continue

            players.append(self.model(**player.data))

        print(f"{len(players)} players loaded")
        self.bulk_create(players, ignore_conflicts=True)


class Player(models.Model):
    class Meta:
        db_table = "players"

    latest_team = models.ForeignKey(Team, related_name='players', null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    player_id = models.CharField(max_length=64, unique=True)
    height = models.CharField(max_length=4)
    weight = models.FloatField(default=0.0)
    position = models.CharField(max_length=4)
    jersey_number = models.IntegerField(default=None)
    draft_pick = models.CharField(max_length=2, default=None)
    draft_year = models.CharField(max_length=4, default=None)
    draft_round = models.CharField(max_length=2, default=None)
    final_year = models.CharField(null=True, blank=True, max_length=4)
    college = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    career_pts_avg = models.FloatField(default=0.0)
    career_reb_avg = models.FloatField(default=0.0)
    career_ast_avg = models.FloatField(default=0.0)

    objects = PlayerModelManager()



