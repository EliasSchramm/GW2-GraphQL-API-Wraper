from enum import Enum
import strawberry


@strawberry.enum
class Product(Enum):
    GUILD_WARS_2 = "GuildWars2"
    HEART_OF_THORNS = "HeartOfThorns"
    PATH_OF_FIRE = "PathOfFire"
