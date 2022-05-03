from typing import List, Optional
import strawberry

from helper.helper import request_api


@strawberry.type
class Mastery:
    name: str
    description: str
    instruction: str
    icon: str
    point_cost: int
    exp_cost: int


@strawberry.type
class MasteryLine:
    id: int
    name: str
    requirement: str
    order: int
    region: str
    background: str
    masteries: List[Mastery]


def _marshal_mastery(mastery: dict) -> Mastery:
    return Mastery(
        name=mastery["name"],
        description=mastery["description"],
        instruction=mastery["instruction"],
        icon=mastery["icon"],
        point_cost=mastery["point_cost"],
        exp_cost=mastery["exp_cost"],
    )


def _marshal_mastery_line(mastery_line: dict) -> MasteryLine:
    return MasteryLine(
        id=mastery_line["id"],
        name=mastery_line["name"],
        requirement=mastery_line["requirement"],
        order=mastery_line["order"],
        region=mastery_line["region"],
        background=mastery_line["background"],
        masteries=[_marshal_mastery(mastery) for mastery in mastery_line["levels"]],
    )


def get_all_mastery_line_ids() -> List[int]:
    return request_api("masteries")


def get_mastery_lines(ids: Optional[List[int]] = []) -> List[MasteryLine]:
    if not ids:
        ids = get_all_mastery_line_ids()

    mastery_lines = request_api(f"masteries?ids={','.join([str(id) for id in ids])}")
    if mastery_lines == {"text": "all ids provided are invalid"}:
        return []

    return [_marshal_mastery_line(mastery_line) for mastery_line in mastery_lines]
