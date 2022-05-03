import requests
import strawberry


BASE_URL = "https://api.guildwars2.com/v2/"


def request_api(endpoint: str) -> dict:
    print("Requesting: " + BASE_URL + endpoint)
    return requests.get(BASE_URL + endpoint, verify=False).json()


@strawberry.input
class Cursor:
    offset: int
    max: int = strawberry.field(
        description="Capped to 200 by default. Higher values will be ignored."
    )
