import random

BOT_PREFIX = "Travis"
BOT_DESCRIPTION = ""
BOT_SEARCH_STRING = "Travis"

KNOWN_GAMES = {"Mastermind": 1, "Checkers": 2}
GAME_READY_PREFIXES = {"Let the game begin!", "On your marks, get set... GO!", "Engines hot!"}

SR_ENERGY_THRESHOLD = 150
SR_DYNAMIC_ENERGY_THRESHOLD = True


def get_game_ready():
    return GAME_READY_PREFIXES[random.randint(0, len(GAME_READY_PREFIXES))]
