from random import Random


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
        pass
    # ○◙☺☻
    # ☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼

    def processmove(self, initial_coords, new_coords, player):
        pass
