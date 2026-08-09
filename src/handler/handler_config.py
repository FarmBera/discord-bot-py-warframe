from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional

from src.constants.keys import (
    ALERTS,
    NEWS,
    SORTIE,
    ARCHONHUNT,
    VOIDTRADERS,
    # STEELPATH,
    DUVIRICYCLE,
    FISSURES,
    ARCHIMEDEA,
    ARCHIMEDEA_DEEP,
    ARCHIMEDEA_TEMPORAL,
    CALENDAR,
    DAILYDEALS,
    INVASIONS,
    DUVIRI_ROTATION,
    DUVIRI_U_K_W,
    DUVIRI_U_K_I,
    EVENTS,
    CETUSCYCLE,
    CAMBIONCYCLE,
    VALLISCYCLE,
    DESCENDIA,
    SEASONINFO,
)
from src.parser.alerts import w_alerts
from src.parser.archimedea import w_deepArchimedea, w_temporalArchimedia
from src.parser.archonHunt import w_archonHunt
from src.parser.calendar import w_calendar
from src.parser.cambionCycle import w_cambionCycle, checkNewCambionState
from src.parser.cetusCycle import w_cetusCycle, checkNewCetusState
from src.parser.dailyDeals import w_dailyDeals, getDarvoRandomMsg
from src.parser.descendia import w_descendia
from src.parser.duviriCycle import w_duviriCycle, checkNewDuviriState
from src.parser.duviriRotation import w_duviri_warframe, w_duviri_incarnon
from src.parser.events import w_events
from src.parser.invasions import w_invasions_se
from src.parser.news import w_news
from src.parser.seasoninfo import w_nightwave
from src.parser.sortie import w_sortie
from src.parser.vallisCycle import w_vallisCycle, checkNewVallisState
from src.parser.voidTraders import w_voidTraders, getBaroRandomMsg


class Logic(Enum):
    """Special handling strategy for each content type.

    DEFAULT is used when a HandlerSpec does not specify a logic;
    it runs `update_check(prev, new)` and parses the whole new object.
    """

    DEFAULT = auto()
    NO_ARGS = auto()  # stateless parser; update_check() takes no arguments
    MISSING = auto()  # notify on newly added items (diff by _id.$oid)
    NEWS = auto()  # like MISSING, but pre-filtered by language
    BOUNTY = auto()  # fetches its own data; skips the shared api cache
    INVASIONS = auto()  # like MISSING, but only invasions with special rewards
    FISSURES = auto()  # save-only; never sends notifications
    VOIDTRADERS = auto()  # multi-event (new schedule / just arrived)
    DEEP_ARCHIMEDEA = auto()
    TEMPORAL_ARCHIMEDEA = auto()
    SEASONINFO = auto()  # notify on newly added Nightwave challenges
    DUVIRI_WARFRAME = auto()  # circuit rotation, CategoryChoices[0]
    DUVIRI_INCARNON = auto()  # circuit rotation, CategoryChoices[1]


@dataclass(frozen=True)
class HandlerSpec:
    """Configuration for a single content type in the notification loop."""

    parser: Optional[Callable] = None
    logic: Logic = Logic.DEFAULT
    update_check: Optional[Callable] = None
    arg_func: Optional[Callable] = None
    # Overrides the DATA_HANDLERS key when reading the api cache / api response
    # (used when multiple handlers share one api object, e.g. ARCHIMEDEA).
    cache_key: Optional[str] = None

    @property
    def needs_cache(self) -> bool:
        """Whether this handler consumes the shared api cache (prev/new objects)."""
        return self.logic not in (Logic.NO_ARGS, Logic.BOUNTY)


# --- shared update_check helpers ---


def _activation_long(item) -> str:
    return item["Activation"]["$date"]["$numberLong"]


def _first_activation_changed(prev, new) -> bool:
    return _activation_long(prev[0]) != _activation_long(new[0])


def _sortie_changed(prev, new) -> bool:
    return (
        prev[0]["_id"]["$oid"] != new[0]["_id"]["$oid"]
        or prev[0]["Activation"]["$date"] != new[0]["Activation"]["$date"]
    )


def _archon_hunt_changed(prev, new) -> bool:
    return prev[0]["Activation"] != new[0]["Activation"]


def _daily_deals_changed(prev, new) -> bool:
    return prev[0]["StoreItem"] != new[0]["StoreItem"]


DATA_HANDLERS: dict = {
    ALERTS: HandlerSpec(parser=w_alerts, logic=Logic.MISSING),
    NEWS: HandlerSpec(parser=w_news, logic=Logic.NEWS),
    CETUSCYCLE: HandlerSpec(
        parser=w_cetusCycle, logic=Logic.NO_ARGS, update_check=checkNewCetusState
    ),
    SORTIE: HandlerSpec(parser=w_sortie, update_check=_sortie_changed),
    ARCHONHUNT: HandlerSpec(parser=w_archonHunt, update_check=_archon_hunt_changed),
    VOIDTRADERS: HandlerSpec(
        parser=w_voidTraders, logic=Logic.VOIDTRADERS, arg_func=getBaroRandomMsg
    ),
    DUVIRICYCLE: HandlerSpec(
        parser=w_duviriCycle, logic=Logic.NO_ARGS, update_check=checkNewDuviriState
    ),
    FISSURES: HandlerSpec(logic=Logic.FISSURES),
    f"{ARCHIMEDEA}{ARCHIMEDEA_DEEP}": HandlerSpec(
        parser=w_deepArchimedea, logic=Logic.DEEP_ARCHIMEDEA, cache_key=ARCHIMEDEA
    ),
    f"{ARCHIMEDEA}{ARCHIMEDEA_TEMPORAL}": HandlerSpec(
        parser=w_temporalArchimedia,
        logic=Logic.TEMPORAL_ARCHIMEDEA,
        cache_key=ARCHIMEDEA,
    ),
    CALENDAR: HandlerSpec(parser=w_calendar, update_check=_first_activation_changed),
    CAMBIONCYCLE: HandlerSpec(
        parser=w_cambionCycle, logic=Logic.NO_ARGS, update_check=checkNewCambionState
    ),
    DAILYDEALS: HandlerSpec(
        parser=w_dailyDeals,
        update_check=_daily_deals_changed,
        arg_func=getDarvoRandomMsg,
    ),
    INVASIONS: HandlerSpec(parser=w_invasions_se, logic=Logic.INVASIONS),
    f"{DUVIRI_ROTATION}{DUVIRI_U_K_W}": HandlerSpec(  # circuit-warframe
        parser=w_duviri_warframe,
        logic=Logic.DUVIRI_WARFRAME,
        cache_key=DUVIRI_ROTATION,
    ),
    f"{DUVIRI_ROTATION}{DUVIRI_U_K_I}": HandlerSpec(  # circuit-incarnon
        parser=w_duviri_incarnon,
        logic=Logic.DUVIRI_INCARNON,
        cache_key=DUVIRI_ROTATION,
    ),
    EVENTS: HandlerSpec(parser=w_events, logic=Logic.MISSING),
    VALLISCYCLE: HandlerSpec(
        parser=w_vallisCycle, logic=Logic.NO_ARGS, update_check=checkNewVallisState
    ),
    # BOUNTY: HandlerSpec(parser=w_bounty, logic=Logic.BOUNTY),
    DESCENDIA: HandlerSpec(parser=w_descendia, update_check=_first_activation_changed),
    SEASONINFO: HandlerSpec(parser=w_nightwave, logic=Logic.SEASONINFO),
}
