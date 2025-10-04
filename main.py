import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="5911!", intents=intents)

# Load saved role id (if any)
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
else:
    config = {"dm_role": None}


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.command()
async def dm(ctx, role_id: int):
    """Set the role whose members will receive war DMs."""
    role = ctx.guild.get_role(role_id)
    if not role:
        return await ctx.send("❌ Invalid role ID.")

    config["dm_role"] = role_id
    with open("config.json", "w") as f:
        json.dump(config, f)

    await ctx.send(f"✅ DM role set to **{role.name}** ({role.id})")


@bot.command()
async def war(ctx):
    """Create and send war embed to role members."""
    if not config.get("dm_role"):
        return await ctx.send("❌ No DM role set. Use `5911!dm <role_id>` first.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("⚔️ Enter **Allies**:")
    allies = (await bot.wait_for("message", check=check)).content

    await ctx.send("💀 Enter **Opps**:")
    opps = (await bot.wait_for("message", check=check)).content

    await ctx.send("🌐 Enter **Server IP**:")
    server_ip = (await bot.wait_for("message", check=check)).content

    # Create embed
    embed = discord.Embed(
        title="🔥 War Alert!",
        color=discord.Color.red()
    )
    embed.add_field(name="Allies", value=allies, inline=False)
    embed.add_field(name="Opps", value=opps, inline=False)
    embed.add_field(name="Server IP", value=server_ip, inline=False)
    embed.set_footer(text=f"Sent by {ctx.author.display_name}")

    # DM everyone with the role
    role = ctx.guild.get_role(config["dm_role"])
    if not role:
        return await ctx.send("❌ Saved role not found in this server.")

    sent, failed = 0, 0
    await ctx.send(f"📨 Sending DMs to members with role `{role.name}`...")

    for member in role.members:
        try:
            await member.send(embed=embed)
            sent += 1
        except:
            failed += 1

    await ctx.send(f"✅ Sent to {sent} members, ❌ failed for {failed}.")


# Run the bot
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN not found in .env file.")
else:
    bot.run(TOKEN)
