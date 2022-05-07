from typing import List, Optional
from uuid import UUID
import requests
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
import warnings
from helper.helper import Cursor
from api.achievements import (
    Achievement,
    AchievementGroup,
    DailyAchievement,
    DailyAchievements,
    get_achievement_groups,
    get_achievements,
    get_all_achievement_group_ids,
    get_all_achievement_ids,
    get_daily_achievements,
)

from api.masteries import MasteryLine, get_all_mastery_line_ids, get_mastery_lines


warnings.filterwarnings("ignore")


@strawberry.type
class Query:
    @strawberry.field
    def mastery_line_ids(self) -> List[int]:
        return get_all_mastery_line_ids()

    @strawberry.field
    def mastery_line(self, ids: Optional[List[int]] = []) -> List[MasteryLine]:
        return get_mastery_lines(ids)

    @strawberry.field
    def achievement_ids(self) -> List[int]:
        return get_all_achievement_ids()

    @strawberry.field
    def achievement(
        self, ids: Optional[List[int]] = [], cursor: Optional[Cursor] = None
    ) -> List[Achievement]:
        max = 200
        offset = 0

        if cursor:
            max = cursor.max
            offset = cursor.offset

        return get_achievements(ids, offset, max)

    @strawberry.field
    def achievementGroupIds(self) -> List[UUID]:
        return get_all_achievement_group_ids()

    @strawberry.field
    def achievementGroup(self) -> List[AchievementGroup]:
        return get_achievement_groups()

    @strawberry.field
    def dailyAchievements(self, tomorrow: Optional[bool] = False) -> DailyAchievements:
        return get_daily_achievements(tomorrow)


schema = strawberry.Schema(query=Query)

print(schema.as_str())

graphql_app = GraphQL(schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
