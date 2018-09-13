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
