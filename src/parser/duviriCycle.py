import datetime as dt

import discord

from src.translator import ts
from src.utils.times import convert_remain

SEED_TIME: str = "2023-01-01T00:00:00+00:00"
SECONDS_PER_MOOD: int = 7200
NEXT_MOOD_LIMIT: int = 2

MOODS = ["fear", "joy", "anger", "envy", "sorrow"]
MOOD_COLOR = {
    "fear": 0xB783C9,
    "joy": 0x2BB8BE,
    "anger": 0xFC8408,
    "envy": 0x69B124,
    "sorrow": 0x6694E6,
}

pf: str = "cmd.duviri-cycle."


def which_mood(timestamp: int) -> int:
    """the index of the current mood based on the timestamp

    :param timestamp: input timestamp
    :return: index of the current mood
    """
    try:
        date = dt.datetime.fromisoformat(SEED_TIME)
        start_time = int(date.timestamp())
    except ValueError:
        print("[ERROR]: Invalid SEED_TIME format")
        start_time = 0

    # calculate diff with current time & seed time
    cycle_length = SECONDS_PER_MOOD * len(MOODS)

    # Adjust if the difference is negative to prevent negative modulo operations
    time_diff = (timestamp - start_time) % cycle_length

    # calculate index
    if time_diff < SECONDS_PER_MOOD:
        return 0
    elif time_diff < (SECONDS_PER_MOOD * 2):
        return 1
    elif time_diff < (SECONDS_PER_MOOD * 3):
        return 2
    elif time_diff < (SECONDS_PER_MOOD * 4):
        return 3
    elif time_diff < (SECONDS_PER_MOOD * 5):
        return 4
    else:
        return 99


def get_next_shift(curr_time: int) -> int:
    """Calculate the next mood-change time
    (sorted in 7,200-second (2-hour) intervals)

    :param curr_time: current timestamp
    :return: next mood change time
    """
    return curr_time + (7200 - (curr_time % 7200))


def get_current_mood() -> dict:
    """
    :return: the current mood state and the expiration time (next mood start time)
    """
    curr_timestamp = int(dt.datetime.now(dt.timezone.utc).timestamp())

    # caltulate state based on current time
    mood_idx = which_mood(curr_timestamp)
    mood_now = MOODS[mood_idx] if mood_idx < len(MOODS) else "Unknown"

    return {"timestamp": get_next_shift(curr_timestamp), "mood": mood_now}


def get_next_mood() -> list[dict]:
    """
    :return: list of mood changes after the given time
    """
    now_stamp = int(dt.datetime.now(dt.timezone.utc).timestamp())
    next_timestamp = get_next_shift(now_stamp)
    mood_list = []

    for i in range(NEXT_MOOD_LIMIT):
        this_time = next_timestamp

        # if not the first, add SECONDS_PER_MOOD to the previous item's time
        if i != 0:
            last_item = mood_list[-1]
            this_time = last_item["timestamp"] + SECONDS_PER_MOOD

        mood_idx = which_mood(this_time)
        this_mood = MOODS[mood_idx] if mood_idx < len(MOODS) else "Unknown"
        mood_list.append({"timestamp": this_time, "mood": this_mood})

    return mood_list


previous_state_duviri = get_current_mood()["mood"]


def checkNewDuviriState():
    global previous_state_duviri
    current = get_current_mood()["mood"]
    if previous_state_duviri != current:
        previous_state_duviri = current
        return True
    return False


def w_duviriCycle() -> tuple[discord.Embed, str]:
    duviri: dict = get_current_mood()
    nextd: list = get_next_mood()

    mood: str = duviri["mood"]

    output_msg: str = ts.get(f"{pf}output").format(
        state=ts.get(f"{pf}{mood}"), time=convert_remain(duviri["timestamp"])
    )
    # next moods
    for item in nextd:
        output_msg += (
            f"{convert_remain(item['timestamp'])} **{ts.get(f'{pf}{item['mood']}')}**\n"
        )

    embed = discord.Embed(description=output_msg.strip(), color=MOOD_COLOR[mood])
    embed.set_thumbnail(url="attachment://i.webp")
    return embed, mood


# print("--- Current Mood ---")
# print(get_current_mood())
# print("\n--- Next Moods ---")
# print(get_next_mood())
# print(w_duviriCycle()[0].description)

# print(checkNewDuviriState())
