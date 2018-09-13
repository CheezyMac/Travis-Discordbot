import mastermind
import checkers

BOT_PREFIX = "Travis"
BOT_DESCRIPTION = ""
BOT_SEARCH_STRING = "Travis"
BOT_TEST_MODE = False

KNOWN_GAMES = {"MASTERMIND": mastermind.create_game, "CHECKERS": checkers.create_game}

GAME_READY_ANNOUNCEMENTS = ["Let the game begin! Head on over to the _**{}**_ channel to play",
                            "On your marks, get set... GO! Head on over to the _**{}**_ channel to play",
                            "Engines hot! Visit the _**{}**_ channel to start"]

COMMANDS = {"play": ">PLAY "}

SR_ENERGY_THRESHOLD = 150
SR_DYNAMIC_ENERGY_THRESHOLD = True
