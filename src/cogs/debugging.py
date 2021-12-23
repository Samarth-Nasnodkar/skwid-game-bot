import discord
from discord.ext import commands
from src.constants.default_perms import default_perms


def get_guild_permissions(member: discord.Member) -> list:
    perms = dict(member.guild_permissions)
    missing_permissions = []
    for perm in default_perms:
        if not perms[perm["perm"]]:
            missing_permissions.append({
                "name": perm["repr"],
                "optional": perm["optional"]
            })

    return missing_permissions


# def get_channel_permissions(user: discord.Member, channel: discord.TextChannel) -> list:
#     perms = dict(channel.permissions_for(user))
#     print(f"Channel perms : {perms}")
#     missing_permissions = []
#     for perm in default_perms:
#         if not perms[perm["perm"]]:
#             missing_permissions.append({
#                 "name": perm["repr"],
#                 "optional": perm["optional"]
#             })
#
#     return missing_permissions


class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="debug")
    async def debug(self, ctx: commands.Context):
        missing_guild_perms = get_guild_permissions(ctx.guild.me)
        # missing_channel_perms = get_channel_permissions(ctx.author, ctx.channel)
        if len(missing_guild_perms) == 0:
            await ctx.send("**All Good** :)")
        else:
            desc = ""
            # if len(missing_channel_perms) > 0:
            #     desc += "**Permissions for** {}:\n============\n".format(ctx.channel.mention)
            #     for perm in missing_channel_perms:
            #         desc += f"**{perm['name']}**"
            #         desc += " `(Optional)`\n" if perm["optional"] else "\n"
            #
            #     desc += "============\n"
            if len(missing_guild_perms) > 0:
                # desc += "**Server Wide Permissions**:\n"
                for perm in missing_guild_perms:
                    desc += f"**{perm['name']}**"
                    desc += " `(Optional)`\n" if perm["optional"] else "\n"

                # desc += "============\n"
            embed = discord.Embed(
                title="Missing Permissions",
                description=desc,
                color=discord.Color.blue()
            ).set_footer(text="Be sure to check the permissions for the channel you're in.")
            await ctx.send(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Debug(client))
