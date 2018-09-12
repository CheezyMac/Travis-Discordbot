import configuration as cfg    # Import configuration settings
import discord          # Import discord API
import features

client = discord.Client()
print(discord.__version__)
active_games = []


@client.event
async def on_message(message):
    # Ignore messages sent by ourselves
    if message.author == client.user:
        return

    # Check if message should be routed to any active games
    for game in active_games:
        if game.game_channel == message.channel:
            ret_code = await game.handlemessage(message)
            if ret_code == 2:  # if game complete, remove from active games
                active_games.remove(game)
                return
            elif ret_code == 0:  # If game did not handle message, continue processing
                continue

    if message.content.upper().startswith("TRAVIS, PLAY "):
        game = await features.creategame(message.content.upper()[13:], client, message)
        if game != -1:
            active_games.append(game)
        return

    if cfg.BOT_SEARCH_STRING.upper() in message.content.upper():
        print("{} mentioned something I'm interested in!".format(message.author))


@client.event
async def on_ready():
    print("Bot ready!")
    print("Logged in as {} ({})".format(client.user.name, client.user.id))

client.run(cfg.BOT_TOKEN)
