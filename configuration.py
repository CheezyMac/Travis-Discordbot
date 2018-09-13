import mastermind
import checkers

BOT_PREFIX = "Travis"
BOT_DESCRIPTION = ""
BOT_SEARCH_STRING = "Travis"

KNOWN_GAMES = {"Mastermind": mastermind.create_game, "Checkers": checkers.create_game}

GAME_READY_PREFIXES = {"Let the game begin! Head on over to the _**{}**_ channel to play",
                       "On your marks, get set... GO! Head on over to the _**{}**_ channel to play",
                       "Engines hot! Visit the _**{}**_ channel to start"}

COMMANDS = {"play": ">PLAY "}

SR_ENERGY_THRESHOLD = 150
SR_DYNAMIC_ENERGY_THRESHOLD = True
