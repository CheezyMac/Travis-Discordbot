from random import Random
from math import floor


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
                return 0
        else:
            player_piece = "X"
            if self.mid_round:
                return 0

        start_position = self.convert_coordinates(coordinates[0])

        # Enforce moving own pieces
        if self.board[start_position[0]][start_position[1]].upper() != player_piece:
            return -1

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
                return -1
            start_position = end_position

            # Check if the piece should be crowned
            if end_position[0] == 7 or end_position[0] == 0:
                player_piece = player_piece.upper()

        # Commit the changes to board
        for item in board_changes:
            self.board[item[0]][item[1]] = item[2]

        # Check for win state

        # Check for deadlock

        # Increment the turn counter & swap players
        if self.mid_round:
            self.moves += 1
            self.mid_round = False
        else:
            self.mid_round = True

        return 1

    def validate_move(self, start_position, end_position, player_piece):
        # Positions of form (vert, horiz)
        # Should return either [(vert,horiz,val),...] or [-1]

        # Ensure destination is not occupied
        if self.board[end_position[0]][end_position[1]] != " ":
            return -1

        d_vert = end_position[0]-start_position[1]
        d_horiz = end_position[1]-start_position[1]
        changes = [(start_position[0], start_position[1], " ")]

        # Enforce valid movement distances
        if d_vert == 0 or abs(d_vert) >= 2:
            return -1
        else:
            if start_position[0] % 2 == 0:
                if not (abs(d_vert) == 1 and -1 <= d_horiz <= 0) and not (abs(d_vert) == 2 and (abs(d_horiz) == 1)):
                    return -1
                else:
                    pass
            else:
                if not (abs(d_vert) == 1 and 0 <= d_horiz <= 1) and not (abs(d_vert) == 2 and (abs(d_horiz) == 1)):
                    return -1
                else:
                    pass



        return -1

    @staticmethod
    def convert_coordinates(coordinate_string):
        raw_coords = coordinate_string.split("")
        vertical = int(raw_coords[1]) - 1
        horizontal = int(raw_coords[0].upper()) - int("A")

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
