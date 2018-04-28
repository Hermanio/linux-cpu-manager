from enum import Enum


class Action(Enum):
    THROTTLE_MODERATE = 1
    THROTTLE_CRITICAL = 2
    BOOST_MODERATE = 3
    BOOST_CRITICAL = 4
    NO_OP = 5
