from discord import PermissionOverwrite, ChannelType
from game import Game
from math import floor
import configuration as cfg


async def create_game(client, message):
    # Get the second player
    join_request = await client.send_message(message.channel, "One more player needed. "
                                                              "Reply '>Join' in 30 seconds to join")
    reply = await client.wait_for_message(timeout=30, channel=message.channel, content=">join")
    if reply is None:
        # Delete the call for players, & close the game
        await client.send_message(message.channel, "Game cancelled: Player timeout reached")
        await client.delete_message(join_request)
        return -1
    if not cfg.BOT_TEST_MODE:
        # Create a game channel
        default_permissions = PermissionOverwrite(read_messages=False)
        player_permissions = PermissionOverwrite(read_messages=True)
        channel = await client.create_channel(message.server, 'checkers',
                                              (message.server.default_role, default_permissions),
                                              (message.server.me, player_permissions),
                                              (message.author, player_permissions), (reply.author, player_permissions),
                                              type=ChannelType.text)
    else:
        channel = message.channel
    checkers = Checkers(client, channel, message.channel, [message.author, message.author])
    await checkers.announcerules()

    return checkers, "checkers"


class Checkers(Game):

    name = "checkers"
    player_count = 2

    def __init__(self, client, game_channel, host_channel, players):
        if len(players) != self.player_count:
            print("Invalid player count in Checkers!")
            self.ready = False
            return
        self.engine = CheckersEngine(players)
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

        for coordinate_string in coordinates:
            # Enforce code length
            if len(coordinate_string) != 2:
                self.message_bin.append(self.client.send_message(self.game_channel,
                                                                 "{} is not a valid coordinate! Try again"
                                                                 .format(coordinate_string)))
                return -1

            working = coordinate_string.upper()#.split('')
            print(working)

            # Enforce value restrictions
            if not (ord("A") <= ord(working[0]) <= ord("H")):
                self.message_bin.append(await self.client.send_message(self.game_channel,
                                                                 "{} is outside board! Try again"
                                                                 .format(working[0])))
                return -1

            if not (1 <= int(working[1]) <= 8):
                self.message_bin.append(await self.client.send_message(self.game_channel,
                                                                 "{} is outside board! Try again"
                                                                 .format(working[1])))
                return -1

        # Try to make the move
        print("Processing move with coords: {}".format(coordinates))
        ret_code = self.engine.processmove(coordinates, message.author)

        # Check if successful
        if ret_code == -1:
            await self.client.send_message(self.game_channel, "Sorry, {}, it's not your turn"
                                     .format(message.author.mention))
            return -1
        elif ret_code == -2:
            await self.client.send_message(self.game_channel, "Illegal move! Try again.")
            return -1
        elif ret_code > 0:
            await self.gamecomplete(ret_code)
            return 2

        # Change the active player
        if self.engine.mid_round:
            self.active_player = self.engine.player_two
        else:
            self.active_player = self.engine.player_one

        # delete the messages and update the board
        for item in self.message_bin:
            self.client.delete_message(item)
        self.message_bin.clear()
        await self.client.edit_message(self.board_message, self.render_board())
        self.message_bin.append(self.client.send_message(self.game_channel, "{}'s turn".format(self.active_player)))

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
        if not cfg.BOT_TEST_MODE:
            await self.client.delete_channel(self.game_channel)

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
        output.append("  ---------------------------------\n")
        output.append("    a   b   c   d   e   f   g   h```")

        return ''.join(output)


class CheckersEngine:

    def __init__(self, players):
        self.player_one = players[0]
        self.player_two = players[1]
        self.player_one_pieces = 12
        self.player_two_pieces = 12
        self.mid_round = False
        self.moves = 0
        self.board = [
            ['x', 'x', 'x', 'x'],
            ['x', 'x', 'x', 'x'],
            ['x', 'x', 'x', 'x'],
            [' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' '],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o']
        ]

    def processmove(self, coordinates, player):

        # Enforce player turns
        if self.player_two == player:
            player_piece = "O"
            if not self.mid_round:
                return -1
        else:
            player_piece = "X"
            if self.mid_round:
                return -1

        start_position = self.convert_coordinates(coordinates[0])

        # Enforce moving own pieces
        if self.board[start_position[0]][start_position[1]].upper() != player_piece:
            return -2

        player_piece = self.board[start_position[0]][start_position[1]]

        board_changes = []
        for i in range(1, len(coordinates)):
            end_position = self.convert_coordinates(coordinates[i])
            results = self.validate_move(start_position, end_position, player_piece)

            # Add changes to queue if move possible, otherwise cancel move
            if results != -1:
                for item in results:
                    board_changes.append(item)
            else:
                return -2
            start_position = end_position

            # Check if the piece should be crowned
            if end_position[0] == 7 or end_position[0] == 0:
                player_piece = player_piece.upper()

        # Commit the changes to board
        for item in board_changes:
            self.board[item[0]][item[1]] = item[2]

        # Check for win state
        pieces = {" ": 0, "X": 0, "O": 0}
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                pieces[self.board[row][column].upper()] += 1
        if pieces["X"] == 0:
            return 2
        elif pieces["O"] == 0:
            return 1

        # Increment the turn counter & swap players
        if self.mid_round:
            self.moves += 1
            self.mid_round = False
        else:
            self.mid_round = True

        return 0

    def validate_move(self, start_position, end_position, player_piece):
        # Positions of form (vert, horiz)
        # Should return either [(vert,horiz,val),...] or [-1]

        # Ensure destination is not occupied
        if self.board[end_position[0]][end_position[1]] != " ":
            return -1

        d_vert = end_position[0]-start_position[1]
        d_horiz = end_position[1]-start_position[1]
        changes = [(start_position[0], start_position[1], " "), (end_position[0], end_position[1], player_piece)]

        # Enforce valid movement direction
        if not player_piece.isupper():
            if d_vert < 0 and player_piece == "x":
                return -1
            elif d_vert > 0 and player_piece == "o":
                return -1

        # Enforce valid movement distances
        if d_vert == 0 or abs(d_vert) >= 2:
            return -1
        else:
            if start_position[0] % 2 == 0:
                if not (abs(d_vert) == 1 and -1 <= d_horiz <= 0) and not (abs(d_vert) == 2 and (abs(d_horiz) == 1)):
                    return -1
                else:
                    if abs(d_vert) == 2:
                        if d_horiz == 1:
                            hopped_piece = self.board[start_position[0]+d_vert/2][start_position[1]].upper()
                            # Ensure hopping over opponent pieces only
                            if hopped_piece == " " or hopped_piece == player_piece.upper():
                                return -1
                            else:
                                changes.append((start_position[0]+d_vert/2, start_position[1], " "))
                        elif d_horiz == -1:
                            hopped_piece = self.board[start_position[0] + d_vert / 2][start_position[1]-1].upper()
                            # Ensure hopping over opponent pieces only
                            if hopped_piece == " " or hopped_piece == player_piece.upper():
                                return -1
                            else:
                                changes.append((start_position[0] + d_vert / 2, start_position[1]-1, " "))
                    else:  # If not jumping, move validation complete
                        return changes
            else:
                if not (abs(d_vert) == 1 and 0 <= d_horiz <= 1) and not (abs(d_vert) == 2 and (abs(d_horiz) == 1)):
                    return -1
                else:
                    if abs(d_vert) == 2:
                        if d_horiz == 1:
                            hopped_piece = self.board[start_position[0] + d_vert / 2][start_position[1] + 1].upper()
                            # Ensure hopping over opponent pieces only
                            if hopped_piece == " " or hopped_piece == player_piece.upper():
                                return -1
                            else:
                                changes.append((start_position[0] + d_vert / 2, start_position[1] + 1, " "))
                        elif d_horiz == -1:
                            hopped_piece = self.board[start_position[0] + d_vert / 2][start_position[1]].upper()
                            # Ensure hopping over opponent pieces only
                            if hopped_piece == " " or hopped_piece == player_piece.upper():
                                return -1
                            else:
                                changes.append((start_position[0] + d_vert / 2, start_position[1], " "))
                    else:  # If not jumping, move validation complete
                        return changes
        return -1

    @staticmethod
    def convert_coordinates(coordinate_string):
        vertical = int(coordinate_string[1]) - 1
        horizontal = ord(coordinate_string[0].upper()) - ord("A")

        if horizontal % 2 != 0:
            if vertical % 2 != 0:
                return vertical, int(floor(float(horizontal)/2.0))
            else:
                return -1
        else:
            if vertical % 2 != 0:
                return -1
            else:
                return vertical, int(floor(float(horizontal) / 2.0))
