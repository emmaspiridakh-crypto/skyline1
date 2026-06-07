import discord
from discord.ext import commands
from discord import app_commands
import json, os
from config import TOKEN, PREFIX
from keep_alive import keep_alive

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ── Data ─────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)

def load_data(filename):
    path = f"data/{filename}.json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path) as f:
        return json.load(f)

def save_data(filename, data):
    with open(f"data/{filename}.json", "w") as f:
        json.dump(data, f, indent=4)

bot.load_data  = load_data
bot.save_data  = save_data

# ── Cogs ─────────────────────────────────────────────────────
COGS = [
    "cogs.tickets",
    "cogs.billing",
    "cogs.reviews",
    "cogs.moderation",
    "cogs.logs",
    "cogs.voice",
    "cogs.utils",
]

@bot.event
async def on_ready():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog}")
        except Exception as e:
            print(f"❌ {cog}: {e}")
    await bot.tree.sync()
    print(f"🤖 {bot.user} | Servers: {len(bot.guilds)}")

keep_alive()
bot.run(TOKEN)
