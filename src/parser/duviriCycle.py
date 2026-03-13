import datetime as dt
from dataclasses import dataclass
from enum import IntEnum

import discord

from src.translator import ts as _ts, language as _default_lang
from src.utils.emoji import worldstate_emoji
from src.utils.times import convert_remain


class Mood(IntEnum):
    FEAR = 0
    JOY = 1
    ANGER = 2
    ENVY = 3
    SORROW = 4

    @property
    def label(self) -> str:
        return self.name.lower()

    @property
    def color(self) -> int:
        return _MOOD_COLORS[self]


_MOOD_COLORS: dict[Mood, int] = {
    Mood.FEAR: 0xB783C9,
    Mood.JOY: 0x2BB8BE,
    Mood.ANGER: 0xFC8408,
    Mood.ENVY: 0x69B124,
    Mood.SORROW: 0x6694E6,
}


@dataclass(frozen=True)
class DuviriCycleConfig:
    origin: dt.datetime = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
    interval: int = 7200  # seconds per state phase


@dataclass(frozen=True)
class State:
    state: Mood
    expires_at: int


class DuviriStateCycle:
    def __init__(self, config: DuviriCycleConfig | None = None):
        self.config = config or DuviriCycleConfig()
        self.origin_timestamp = int(self.config.origin.timestamp())
        self.total_cycle = self.config.interval * len(Mood)
        self.prev_state: Mood | None = None

    @staticmethod
    def stamp() -> int:
        return int(dt.datetime.now(dt.timezone.utc).timestamp())

    def state_at(self, timestamp: int) -> Mood:
        """Determine the active state at a given unix timestamp."""
        elapsed = (timestamp - self.origin_timestamp) % self.total_cycle
        index = elapsed // self.config.interval
        return Mood(min(index, len(Mood) - 1))

    def next_timestamp(self, timestamp: int) -> int:
        """Unix timestamp of the next state transition after `timestamp`."""
        remainder = timestamp % self.config.interval
        return timestamp + (self.config.interval - remainder)

    def current(self) -> State:
        now = self.stamp()
        return State(
            state=self.state_at(now),
            expires_at=self.next_timestamp(now),
        )

    def upcoming(self, count: int = 4) -> list[State]:
        boundary = self.next_timestamp(self.stamp())
        return [
            State(
                state=self.state_at(boundary + i * self.config.interval),
                expires_at=boundary + i * self.config.interval,
            )
            for i in range(count)
        ]

    def is_changed(self) -> bool:
        current_state = self.current().state
        changed = self.prev_state is not None and self.prev_state != current_state
        self.prev_state = current_state
        return changed


# Module-level singleton
duviri_cycle = DuviriStateCycle()

pf: str = "cmd.duviri-cycle."


def w_duviriCycle(ts=_ts, lang=_default_lang) -> tuple[discord.Embed, str]:
    state = duviri_cycle.current()
    upcoming = duviri_cycle.upcoming()
    label = state.state.label

    output_msg: str = ts.get(f"{pf}output").format(
        state=f"{ts.get(f'{pf}{label}')}{worldstate_emoji.get(label, '')}",
        time=convert_remain(state.expires_at),
    )

    for item in upcoming:
        item_label = item.state.label
        output_msg += (
            f"{convert_remain(item.expires_at)} **{ts.get(f'{pf}{item_label}')}**\n"
        )

    embed = discord.Embed(description=output_msg.strip(), color=state.state.color)
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, label


def checkNewDuviriState() -> bool:
    return duviri_cycle.is_changed()


# print(w_duviriCycle()[0].description)
