from enum import Enum
from typing import List, Optional
from requests import PreparedRequest
import strawberry
from api.general import Product
from helper.helper import request_api


@strawberry.enum
class AchievementFlag(Enum):
    PVP = "Pvp"
    CATEGORY_DISPLAY = "CategoryDisplay"
    MOVE_TO_TOP = "MoveToTop"
    IGNORE_NEARLY_COMPLETE = "IgnoreNearlyComplete"
    REPEATABLE = "Repeatable"
    HIDDEN = "Hidden"
    REQUIRES_UNLOCK = "RequiresUnlock"
    REPAIR_ON_LOGIN = "RepairOnLogin"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    PERMANENT = "Permanent"


@strawberry.type
class AchievementTier:
    count: int
    points: int


@strawberry.type
class AchievementTextBit:
    text: str


@strawberry.type
class AchievementBitNotImplemented:
    msg: str


@strawberry.type
class Achievement:
    id: int
    name: str
    description: str
    requirement: str
    locked_text: str
    flags: List[AchievementFlag]
    tiers: List[AchievementTier]
    prerequisites: List[
        Optional[
            strawberry.LazyType(
                "Achievement", "api.achievements", package="achievements"
            )
        ]
    ]
    bits: Optional[List[AchievementTextBit | AchievementBitNotImplemented]]
    point_cap: Optional[int]


@strawberry.type
class LevelCap:
    min: int
    max: int


@strawberry.type
class DailyAchievement(Achievement):
    level: LevelCap
    required_access: List[Product]


@strawberry.type
class DailyAchievements:
    pve: List[DailyAchievement]
    pvp: List[DailyAchievement]
    wvw: List[DailyAchievement]
    fractals: List[DailyAchievement]
    special: List[DailyAchievement]


def _marshal_achievement_bit(
    bit: dict,
) -> AchievementTextBit | AchievementBitNotImplemented:
    if bit["type"] == "Text":
        return AchievementTextBit(bit["text"])
    return AchievementBitNotImplemented(msg="nope")


def _marshal_achievement_tier(tier: dict) -> AchievementTier:
    return AchievementTier(count=tier["count"], points=tier["points"])


def _marshal_achievement(achievement: dict, achievement_map: dict) -> Achievement:
    return Achievement(
        id=achievement["id"],
        name=achievement["name"],
        description=achievement["description"],
        requirement=achievement["requirement"],
        locked_text=achievement["locked_text"],
        flags=achievement["flags"],
        tiers=[_marshal_achievement_tier(tier) for tier in achievement["tiers"]],
        prerequisites=[
            _marshal_achievement(achievement_map[id], achievement_map)
            for id in achievement.get("prerequisites", [])
        ],
        point_cap=achievement.get("point_cap", None),
        bits=[_marshal_achievement_bit(bit) for bit in achievement.get("bits", [])],
    )


def _marshal_level_cap(level: dict) -> LevelCap:
    return LevelCap(min=level["min"], max=level["max"])


def _marshal_daily_achievement(
    achievement: dict, achievement_map: dict
) -> DailyAchievement:
    _ = _marshal_achievement(achievement_map[achievement["id"]], achievement_map)

    return DailyAchievement(
        id=_.id,
        bits=_.bits,
        description=_.description,
        flags=_.flags,
        level=_marshal_level_cap(achievement["level"]),
        locked_text=_.locked_text,
        name=_.name,
        point_cap=_.point_cap,
        prerequisites=_.prerequisites,
        required_access=achievement["required_access"],
        requirement=_.requirement,
        tiers=_.tiers,
    )


def get_all_achievement_ids() -> List[int]:
    return request_api("achievements")


def _get_achievements(
    ids: Optional[List[int]] = [], offset: int = 0, max: int = 200
) -> List[dict]:
    if not ids:
        ids = get_all_achievement_ids()

    if len(ids) >= max:
        ids = ids[offset : offset + max]

    achievements = request_api(f"achievements?ids={','.join([str(id) for id in ids])}")
    if achievements == {"text": "all ids provided are invalid"}:
        return []

    prerequisite_achievement_ids = [
        id
        for achievement in achievements
        for id in achievement.get("prerequisites", [])
    ]

    if prerequisite_achievement_ids:
        achievements += _get_achievements(prerequisite_achievement_ids)

    return achievements


def get_achievements(
    ids: Optional[List[int]] = [], offset: int = 0, max: int = 200
) -> List[Achievement]:
    achievements = _get_achievements(ids, offset, max)

    achievement_map = {achievement["id"]: achievement for achievement in achievements}

    return [
        _marshal_achievement(achievement, achievement_map)
        for achievement in achievements
    ]


def get_daily_achievements(tomorrow: bool = False) -> List[DailyAchievements]:
    categories = ["pve", "pvp", "fractals", "wvw", "special"]

    endpoint = "achievements/daily"
    if tomorrow:
        endpoint += "/tomorrow"

    daily_achievements = request_api(endpoint)

    achievement_ids = []
    for category in categories:
        achievement_ids += [daily["id"] for daily in daily_achievements[category]]
    achievement_map = {
        achievement["id"]: achievement
        for achievement in _get_achievements(achievement_ids)
    }

    return DailyAchievements(
        pve=[
            _marshal_daily_achievement(daily, achievement_map)
            for daily in daily_achievements["pve"]
        ],
        pvp=[
            _marshal_daily_achievement(daily, achievement_map)
            for daily in daily_achievements["pvp"]
        ],
        wvw=[
            _marshal_daily_achievement(daily, achievement_map)
            for daily in daily_achievements["wvw"]
        ],
        fractals=[
            _marshal_daily_achievement(daily, achievement_map)
            for daily in daily_achievements["fractals"]
        ],
        special=[
            _marshal_daily_achievement(daily, achievement_map)
            for daily in daily_achievements["special"]
        ],
    )
