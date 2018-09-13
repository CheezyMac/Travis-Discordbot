import speech_recognition as sr
import configuration as cfg
from random import randint

r = sr.Recognizer()
r.energy_threshold = cfg.SR_ENERGY_THRESHOLD
r.dynamic_energy_threshold = cfg.SR_DYNAMIC_ENERGY_THRESHOLD


def get_game_ready():
    return cfg.GAME_READY_ANNOUNCEMENTS[randint(0, len(cfg.GAME_READY_PREFIXES))]


async def list_games(client, channel):
    available_games = []
    column_count = 0
    rows = 0
    for game in cfg.KNOWN_GAMES:
        available_games.append(game)
        column_count += 1
        if column_count == 3:
            available_games.append("\n")
            column_count = 0
            rows += 1
        else:
            available_games.append("\t")
    del available_games[-1]
    available_games = ''.join(available_games)

    await client.send_message(channel, "Sorry, I don't recognize that game. Here are the ones I know:"
                                         "```{}```".format(available_games))
