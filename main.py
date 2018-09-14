import configuration as cfg    # Import configuration settings
import discord          # Import discord API
import features
import sys

if not 2 <= len(sys.argv) <= 3:
    print("Argument error! Please enter only the bot token as argument")
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

    if message.content.upper().startswith(cfg.COMMANDS["play"]):
        name = message.content.upper()[len(cfg.COMMANDS["play"]):]

        if name.upper() in cfg.KNOWN_GAMES:
            payload = await cfg.KNOWN_GAMES[name](client, message)
            if payload != -1:
                active_games.append(payload[0])
                await client.send_message(message.channel, features.get_game_ready().format(payload[1]))
        else:
            await features.list_games(client, message.channel)

    if cfg.BOT_SEARCH_STRING.upper() in message.content.upper():
        print("{} mentioned something I'm interested in!".format(message.author))

        if "PLAY" in message.content.upper():
            print("User wants to play")
            name = message.content.upper().split(" ")[-1]
            print("I think they want to play {}".format(name))
            if name.upper() in cfg.KNOWN_GAMES:
                payload = await cfg.KNOWN_GAMES[name](client, message)
                if payload != -1:
                    active_games.append(payload[0])
                    await client.send_message(message.channel, features.get_game_ready().format(payload[1]))
            else:
                await features.list_games(client, message.channel)


@client.event
async def on_ready():
    print("Bot ready!")
    print("Logged in as {} ({})".format(client.user.name, client.user.id))
if len(sys.argv) == 3:
    cfg.BOT_TEST_MODE = bool(sys.argv[2])
client.run(sys.argv[1])
