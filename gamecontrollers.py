import gameengines


class Game:

    name = ""
    players = []
    player_count = 0
    game_channel = ""
    host_channel = ""

    def __init__(self, client, game_channel, host_channel, players):
        self.client = client
        self.game_channel = game_channel
        self.host_channel = host_channel
        self.players = players

    def announcerules(self):
        pass

    ''' Return codes:
    -1: Error
    0: Message ignored
    1: Successfully processed
    2: Game ended
    '''
    def handlemessage(self, message):
        return 0

    def gamecomplete(self, win_state):
        pass


class Mastermind(Game):
    name = "mastermind"
    player_count = 1

    def __init__(self, client, game_channel, host_channel, players, code_length, repeats_allowed, domain_length, turns):
        if len(players) != self.player_count:
            print("Invalid player count in Mastermind!")
            self.ready = False
            return
        self.engine = gameengines.MastermindEngine(code_length, repeats_allowed, domain_length, turns)
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

        await self.client.delete_channel(self.game_channel)

        # TODO: Add score to the leaderboard


class Checkers(Game):

    name = "checkers"
    player_count = 2

    def __init__(self, client, game_channel, host_channel, players):
        if len(players) != self.player_count:
            print("Invalid player count in Checkers!")
            self.ready = False
            return
        self.engine = gameengines.CheckersEngine(players)
        self.board_message = None
        self.active_player = 0
        self.ready = True
        self.message_bin = []
        Game.__init__(self, client, game_channel, host_channel, players)

    async def announcerules(self):

        await self.client.send_message(self.game_channel, "To make a move, simply type the start & end positions of the"
                                                          " move, including any temporary stops. Start & end are"
                                                          " represented in row column form, i.e A5 or F7")
        await self.client.send_message(self.game_channel, "Please note that your entire move must be in the message for"
                                                          " it to count. If you are jumping over multiple pieces, each"
                                                          " stop should be included in the message")
        await self.client.send_message(self.game_channel, "Example: B4 D6 B8")
        self.board_message = await self.client.send_message(self.game_channel, self.render_board())

    async def handlemessage(self, message):

        # Ignore messages that don't come from players
        if message.author != self.players[self.active_player]:
            pass

        coordinates = message.content.split(" ")
        self.message_bin.append(message)
        valid = False
        for coordinate_string in coordinates:
            # Enforce code length
            if len(coordinate_string) != 2:
                self.message_bin.append(self.client.send_message(self.game_channel,
                                                                 "{} is not a valid coordinate! Try again"
                                                                 .format(coordinate_string)))
                return -1

            working = coordinate_string.upper().split()

            # Enforce value restrictions
            if not (int("A") <= int(working[0]) <= int("F")):
                self.message_bin.append(self.client.send_message(self.game_channel,
                                                                 "{} is outside board! Try again"
                                                                 .format(working[0])))
                return -1

            if not (1 <= int(working[1] <= 8)):
                self.message_bin.append(self.client.send_message(self.game_channel,
                                                                 "{} is outside board! Try again"
                                                                 .format(working[1])))
                return -1

        if valid:
            ret_code = self.engine.processmove(coordinates, message.author)
            if ret_code == 0:
                self.client.send_message(self.game_channel, "Sorry, {}, it's not your turn"
                                         .format(message.author.mention))
                return -1
            elif ret_code == -1:
                self.client.send_message(self.game_channel, "Illegal move! Try again.")
            # delete the message and update the board
            for item in self.message_bin:
                self.client.delete_message(item)
            self.message_bin.clear()
            await self.client.edit_message(self.board_message, self.render_board())
        return 0

    async def gamecomplete(self, win_state):
        if win_state != -1:
            if win_state == 1:
                winner = self.players[1]
                loser = self.players[0]
            else:
                winner = self.players[0]
                loser = self.players[1]
            await self.client.send_message(self.host_channel, "{} defeated {} in {} moves!".format(winner, loser,
                                                                                                   self.engine.moves))
        else:
            await self.client.send_message(self.host_channel, "Game forfeit.")

        await self.client.delete_channel(self.game_channel)
        pass

    def render_board(self):

        b = self.engine.board
        output = []
        output.append("```  ---------------------------------\n")
        output.append("8 |   | {} |   | {} |   | {} |   | {} |\n".format(b[7][0], b[7][1], b[7][2], b[7][3]))
        output.append("  ---------------------------------\n")
        output.append("7 | {} |   | {} |   | {} |   | {} |   |\n".format(b[6][0], b[6][1], b[6][2], b[6][3]))
        output.append("  ---------------------------------\n")
        output.append("6 |   | {} |   | {} |   | {} |   | {} |\n".format(b[5][0], b[5][1], b[5][2], b[5][3]))
        output.append("  ---------------------------------\n")
        output.append("5 | {} |   | {} |   | {} |   | {} |   |\n".format(b[4][0], b[4][1], b[4][2], b[4][3]))
        output.append("  ---------------------------------\n")
        output.append("4 |   | {} |   | {} |   | {} |   | {} |\n".format(b[3][0], b[3][1], b[3][2], b[3][3]))
        output.append("  ---------------------------------\n")
        output.append("3 | {} |   | {} |   | {} |   | {} |   |\n".format(b[2][0], b[2][1], b[2][2], b[2][3]))
        output.append("  ---------------------------------\n")
        output.append("2 |   | {} |   | {} |   | {} |   | {} |\n".format(b[1][0], b[1][1], b[1][2], b[1][3]))
        output.append("  ---------------------------------\n")
        output.append("1 | {} |   | {} |   | {} |   | {} |   |\n".format(b[0][0], b[0][1], b[0][2], b[0][3]))
        output.append("  ---------------------------------")
        output.append("    a   b   c   d   e   f```")

        return ''.join(output)
