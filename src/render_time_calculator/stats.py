import json
import time

STATS_PATH = "data/debug/stats.json"
TIME_PATH = "data/debug/time.json"

DEFAULT_STATS = {
    "totalAnalyzed": 0,
    "totalGPUAnalyzed": 0,
    "perfectMatch": 0,
    "guessedMatch": 0,
    "noMatch": 0
}

TIME_STATS = {
    "startTime": None,
    "endTime": None,
    "totalExecutionTime": 0
}


# ----------------------------------------
# STATS
# ----------------------------------------


def load_stats():
    try:
        with open(STATS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        save_stats(DEFAULT_STATS)


def save_stats(stats):
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)


def increment_stat(name, amount=1):
    stats = load_stats()

    if name not in stats:
        stats[name] = 0

    stats[name] += amount
    save_stats(stats)


def update_stats(new_stats: dict):
    stats = load_stats()

    for name in new_stats:
        stats[name] = stats.get(name, 0) + new_stats[name]

    save_stats(stats)


# ----------------------------------------
# TIME
# ----------------------------------------

def load_time():
    try:
        with open(TIME_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        save_time(TIME_STATS)


def save_time(stats):
    with open(TIME_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)


def start_timer():
    stats = load_time()
    stats["startTime"] = time.time()
    save_time(stats)


def end_timer():
    stats = load_time()

    if stats["startTime"] is None:
        raise AssertionError("Cannot end timer before starting it.")

    stats["endTime"] = time.time()
    stats["totalExecutionTime"] = stats["endTime"] - stats["startTime"]

    save_time(stats)


# def set_time():
#     timestamp = time.time()
#     stats = load_stats()

#     if stats["endTime"] is not None:
#         raise AssertionError("Both Start and End time are full, you can only use this function twice.")

#     if stats["startTime"] is None:
#         stats["startTime"] = timestamp * 1000
#     else:
#         stats["endTime"] = timestamp * 1000
#         stats["totalExecutionTime"] = stats["endTime"] - stats["startTime"]

#     save_stats(stats)


save_stats(DEFAULT_STATS)
save_time(TIME_STATS)
