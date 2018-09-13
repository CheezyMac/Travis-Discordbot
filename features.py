import speech_recognition as sr
import configuration as cfg
import discord
import gamecontrollers

r = sr.Recognizer()
r.energy_threshold = cfg.SR_ENERGY_THRESHOLD
r.dynamic_energy_threshold = cfg.SR_DYNAMIC_ENERGY_THRESHOLD


async def creategame(game, client, message):
    if game == "MASTERMIND":
        # Creates a channel that only the players (And administrators) can see
        default_permissions = discord.PermissionOverwrite(read_messages=False)
        player_permissons = discord.PermissionOverwrite(read_messages=True)
        channel = await client.create_channel(message.server, 'mastermind', (message.server.default_role, default_permissions),
                                              (message.server.me, player_permissons), (message.author, player_permissons),
                                              type=discord.ChannelType.text)
        code_length = 4
        repeats_allowed = False
        domain_length = 9
        turns = 16

        mastermind = gamecontrollers.Mastermind(client, channel, message.channel, [message.author],
                                                code_length, repeats_allowed, domain_length, turns)
        await mastermind.announcerules()
        await client.send_message(message.channel, "Let the game begin! Head over to the mastermind channel to play")
        return mastermind
    elif game == "CHECKERS":
        await client.send_message(message.channel, "Sorry, checkers is under development")
        # Get the second player
        join_request = await client.send_message(message.channel, "One more player needed. "
                                                                  "Reply '>Join' in 30 seconds to join")
        reply = await client.wait_for_message(timeout=30, channel=message.channel, content=">Join")
        if reply.content is None:
            # Delete the call for players, & close the game
            await client.send_message(message.channel, "Game cancelled: Player timeout reached")
            await client.delete_message(join_request)
            return -1

        # Create a game channel
        default_permissions = discord.PermissionOverwrite(read_messages=False)
        player_permissons = discord.PermissionOverwrite(read_messages=True)
        channel = await client.create_channel(message.server, 'checkers',
                                              (message.server.default_role, default_permissions),
                                              (message.server.me, player_permissons),
                                              (message.author, player_permissons), (reply.author, player_permissons),
                                              type=discord.ChannelType.text)
        checkers = gamecontrollers.Checkers(client, channel, message.channel, [message.author, message.author])
        await checkers.announcerules()
        await client.send_message(message.channel, "{} Head over to the checkers channel to play".format(cfg.get_game_ready()))
        return checkers
    else:
        return -1


async def list_games(client, channel):
    available_games = []
    column_count = 0
    rows = 0
    for game in cfg.KNOWN_GAMES:
        available_games.append(game)
        column_count += 1
        if column_count == 3:
            available_games.append("\n")
            column_count = 0
            rows += 1
        else:
            available_games.append("\t")
    del available_games[-1]
    available_games = ''.join(available_games)

    await client.send_message(channel, "Sorry, I don't recognize that game. Here are the ones I know:"
                                         "```{}```".format(available_games))