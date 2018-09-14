from discord import PermissionOverwrite, ChannelType
from game import Game
from random import Random
import configuration as cfg


async def create_game(client, message):
    # Creates a channel that only the players (And administrators) can see
    default_permissions = PermissionOverwrite(read_messages=False)
    player_permissons = PermissionOverwrite(read_messages=True)
    if cfg.BOT_TEST_MODE:
        channel = message.channel
    else:
        channel = await client.create_channel(message.server, 'mastermind', (message.server.default_role, default_permissions),
                                              (message.server.me, player_permissons), (message.author, player_permissons),
                                              type=ChannelType.text)
    code_length = 4
    repeats_allowed = False
    domain_length = 9
    turns = 16

    mastermind = Mastermind(client, channel, message.channel, [message.author], code_length, repeats_allowed, domain_length, turns)
    await mastermind.announcerules()
    return mastermind, "mastermind"


class Mastermind(Game):
    name = "mastermind"
    player_count = 1

    def __init__(self, client, game_channel, host_channel, players, code_length, repeats_allowed, domain_length, turns):
        if len(players) != self.player_count:
            print("Invalid player count in Mastermind!")
            self.ready = False
            return
        self.engine = MastermindEngine(code_length, repeats_allowed, domain_length, turns)
        self.ready = True
        Game.__init__(self, client, game_channel, host_channel, players)

    async def announcerules(self):
        await self.client.send_message(self.game_channel, "Game rules: {} turns, {} digit code, digits 0-{}, repeats {}"
                                       .format(self.engine.max_turns, self.engine.code_length, self.engine.domain_size,
                                               "On" if self.engine.repeats_allowed else "Off"))
        await self.client.send_message(self.game_channel,
                                       "After each guess, I will reply with the number of guesses in the correct "
                                       "positions & correct colours, and with the number of guesses with the correct "
                                       "colours in the form [correct, almost correct]")
        await self.client.send_message(self.game_channel,
                                       "Guesses should be made in the form '##-##-##-##', without quotes")
        # TODO: make format warning obey code length

    async def handlemessage(self, message):

        if message.author == self.players[0]:
            if message.content.upper() == "TERMINATE":
                await self.gamecomplete(False)
                return 2
            else:
                possible_guess = message.content.split("-")

                # Enforce code length
                if len(possible_guess) != self.engine.code_length:
                    await self.client.send_message(self.game_channel, "Your guess must have {} elements! Try again"
                                                   .format(self.engine.code_length))
                    return 1

                guess = []
                # Enforce & convert to numeric symbols
                for element in possible_guess:
                    try:
                        guess.append(int(element))
                    except ValueError:
                        await self.client.send_message(self.game_channel,
                                                       "{} is not a valid number! Try again".format(element))
                        return 1

                # Enforce domain bounds
                for element in guess:
                    if element > self.engine.domain_size:
                        await self.client.send_message(self.game_channel,
                                                       "{} is out of bounds! Try again".format(element))
                        return 1

                # Enforce repeat elements
                if not self.engine.repeats_allowed:
                    for element in guess:
                        if guess.count(element) != 1:
                            await self.client.send_message(self.game_channel,
                                                           "Repeat elements are not allowed! Try again")
                            return 1
                # TODO: more sanity checking

                # Evaluate the guess
                score = self.engine.evaluateguess(guess)

                if self.engine.complete:
                    await self.gamecomplete(self.engine.win_state)
                    return 2
                await self.client.send_message(self.game_channel, "[{}, {}]".format(score[0], score[1]))
                return 1
        else:
            return 0

    async def gamecomplete(self, win_state):
        # Close the game channel & report the scores to the host channel
        if win_state:
            await self.client.send_message(self.host_channel, "{} completed Mastermind in {} turns!\nGame settings:\n"
                                                              "```{} digit code, digits 0-{}, repeats {}```"
                                           .format(self.players[0].mention, self.engine.turns, self.engine.code_length,
                                                   self.engine.domain_size,
                                                   "On" if self.engine.repeats_allowed else "Off"))
        else:
            await self.client.send_message(self.host_channel, "{} failed to completed Mastermind in {} turns.\nGame "
                                                              "settings:\n```{} digit code, digits 0-{}, repeats {}```"
                                           .format(self.players[0].mention, self.engine.turns, self.engine.code_length,
                                                   self.engine.domain_size,
                                                   "On" if self.engine.repeats_allowed else "Off"))
        if not cfg.BOT_TEST_MODE:
            await self.client.delete_channel(self.game_channel)

        # TODO: Add score to the leaderboard


class MastermindEngine:

    def __init__(self, code_length, repeats_allowed, domain_size, max_turns):
        self.code_length = code_length
        self.domain_size = domain_size
        self.code = []
        self.repeats_allowed = repeats_allowed
        self.turns = 0
        self.max_turns = max_turns
        self.complete = False
        self.win_state = False
        rng = Random()
        while len(self.code) < self.code_length:
            value = rng.randint(0, self.domain_size)
            if repeats_allowed or value not in self.code:
                self.code.append(value)

    def evaluateguess(self, guess):
        if len(guess) != self.code_length:
            return -1
        self.turns += 1
        correct = 0
        good = 0

        for i in range(len(guess)):
            if guess[i] == self.code[i]:
                correct += 1
            else:
                if guess[i] in self.code:
                    good += 1

        if correct == self.code_length:
            self.win_state = True
            self.complete = True
        elif self.turns >= self.max_turns:
            self.complete = True

        return [correct, good]
