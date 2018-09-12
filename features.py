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
        default_permissions = discord.PermissionOverwrite(read_messages=False)
        player_permissons = discord.PermissionOverwrite(read_messages=True)
        channel = await client.create_channel(message.server, 'checkers',
                                              (message.server.default_role, default_permissions),
                                              (message.server.me, player_permissons),
                                              (message.author, player_permissons),
                                              type=discord.ChannelType.text)
        checkers = gamecontrollers.Checkers(client, channel, message.channel, [message.author, message.author])
        await checkers.announcerules()
        await client.send_message(message.channel, "Let the game begin! Head over to the checkers channel to play")
        return checkers
    else:
        print(game)
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

        await client.send_message(message.channel, "Sorry, I don't recognize that game. Here are the ones I know:"
                                  "```{}```".format(available_games))
        return -1
