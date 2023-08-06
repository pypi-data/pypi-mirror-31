from enum import Enum
from datetime import datetime
import math
import asyncio
import json

import aiohttp

from ..gametypes import GameType

RAW_ACHIEVEMENTS_URL = \
    "https://raw.githubusercontent.com/HypixelDev" \
    "/PublicAPI/master/Documentation/misc/Achievements.json"


class OneTimeAchievement:
    def __init__(self, data: tuple):
        self.game = data[0]
        self.db_name = data[1]
        self.points = data[2]["points"]
        self.name = data[2]["name"]
        self.description = data[2]["description"]

    def __repr__(self):
        return "<OneTimeAchievement game={0.game} db_name={0.db_name} "\
               "name={0.name} points={0.points} description={0.description}"\
               "".format(self)


class TieredAchievement:
    def __init__(self, data: tuple):
        self.game = data[0]
        self.db_name = data[1]
        self.player_value = data[3]
        self.name = data[2]["name"]
        self.description = data[2]["description"]
        completed_tiers = []
        unfinished_tiers = []
        for tier in data[2]["tiers"]:
            if tier["amount"] <= self.player_value:
                completed_tiers.append(AchievementTier(**tier))
            else:
                unfinished_tiers.append(AchievementTier(**tier))
        self.completed_tiers = completed_tiers
        self.unfinished_tiers = unfinished_tiers


class AchievementTier:
    def __init__(self, tier: int, points: int, amount: int):
        self.tier = tier
        self.points = points
        self.amount = amount


class PixelAchievements:
    achievements = None

    def __init__(self):
        loop = asyncio.get_event_loop()
        future = asyncio.Future()
        asyncio.ensure_future(self.get_all_achievements(future))
        loop.run_until_complete(future)
        self.achievements = future.result()["achievements"]

    @staticmethod
    async def get_all_achievements(future):
        async with aiohttp.ClientSession() as session:
            async with session.get(RAW_ACHIEVEMENTS_URL) as r:
                if r.status == 200:
                    try:
                        data = json.loads(await r.text())
                    except aiohttp.ClientResponseError as e:
                        future.set_exception(e)
                    else:
                        future.set_result(data)
                else:
                    future.set_exception(
                        RuntimeError(
                            "Something went wrong getting all achievements"
                        )
                    )

    def get_one_time_achievement(self, name: str):
        game, achievement_name = name.split("_", 1)
        raw_achievement = \
            self.achievements[game]["one_time"][achievement_name.upper()]
        return OneTimeAchievement((game, achievement_name, raw_achievement))

    def get_tiered_achievement(self, name: str, player_value: int):
        game, achievement_name = name.split("_", 1)
        raw_achv = self.achievements[game]["tiered"][achievement_name.upper()]
        return TieredAchievement(
            (game, achievement_name, raw_achv, player_value)
        )


class PlayerAchievements:

    def __init__(self, data, all_achievements: PixelAchievements):
        self.all_achievements = all_achievements
        total_points = 0
        one_time = []
        tiered = []
        if "achievementsOneTime" in data:
            for item in data["achievementsOneTime"]:
                one_time.append(
                    self.all_achievements.get_one_time_achievement(item)
                )
        if "achievements" in data:
            for k, v in data["achievements"].items():
                tiered.append(
                    self.all_achievements.get_tiered_achievement(k, v)
                )
        self.one_time = one_time
        self.tiered = tiered


class PlayerRank(Enum):
    ADMIN = "Admin"
    MODERATOR = "Moderator"
    HELPER = "Helper"
    JR_HELPER = "Jr. Helper"
    YOUTUBER = "Youtuber"
    BUILD_TEAM = "Build Team"
    SUPERSTAR = "MVP++"
    MVP_PLUS = "MVP+"
    MVP = "MVP"
    VIP_PLUS = "VIP+"
    VIP = "VIP"
    NONE = ""

    def __init__(self, pretty_name: str):
        self.pretty_name = pretty_name

    @classmethod
    def from_player_data(cls, data: dict):
        if "rank" in data:
            return getattr(cls, data["rank"])
        elif data.get("buildTeam") is True:
            return cls.BUILD_TEAM
        elif data.get("monthlyPackageRank") == "SUPERSTAR":
            return cls.SUPERSTAR
        elif "newPackageRank" in data:
            return getattr(cls, data["newPackageRank"])
        elif "packageRank" in data:
            return getattr(cls, data["packageRank"])
        else:
            return cls.NONE


class Player:
    def __init__(self, _id: str, displayname: str, first_login: int,
                 last_login: int, karma: int, network_exp: float,
                 rank: PlayerRank, last_logout: int,
                 achievements: PlayerAchievements, stats: list,
                 most_recent_game_type: GameType):
        self._id = _id
        self.displayname = displayname
        self.first_login = datetime.utcfromtimestamp(first_login/1000)
        self.last_login = datetime.utcfromtimestamp(last_login/1000)
        self.karma = karma
        self.network_exp = network_exp
        self.rank = rank
        self.last_logout = datetime.utcfromtimestamp(last_logout/1000)
        self.achievements = achievements
        self.stats = stats
        self.most_recent_game_type = most_recent_game_type

    def network_level(self) -> float:
        base = 10000
        growth = 2500

        reverse_pq_prefix = -(base - 0.5 * growth) / growth
        reverse_const = math.pow(reverse_pq_prefix, 2)
        growth_divides_2 = 2 / growth

        return 1.0 if self.network_exp < 0 \
            else 1 + reverse_pq_prefix + math.sqrt(
                reverse_const + growth_divides_2 * self.network_exp
            )
