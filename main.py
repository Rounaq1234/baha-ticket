import discord
from discord.ext import commands
import os
import json

# ----------------------------------
# DISABLE ALL DISCORD VOICE FEATURES
# Prevents discord.py from importing audioop (Railway fix)
# ----------------------------------
import discord.voice_client
discord.voice_client.has_nacl = lambda: False


# -----------------------------
# Load Config
# -----------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_json("config.json")


# -----------------------------
# Intents
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True


# -----------------------------
# Bot
# -----------------------------
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=config.get("application_id")
)


# -----------------------------
# Events
# -----------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    try:
        await bot.tree.sync()
        print("✔ Slash commands synced globally.")
    except Exception as e:
        print("❌ Failed to sync commands:", e)


# -----------------------------
# Load Cogs Automatically
# -----------------------------
async def load_all_cogs():
    for folder in ["cogs", "utils"]:
        if not os.path.exists(folder):
            continue

        for filename in os.listdir(folder):
            if filename.endswith(".py"):
                try:
                    await bot.load_extension(f"{folder}.{filename[:-3]}")
                    print(f"Loaded → {folder}.{filename}")
                except Exception as e:
                    print(f"Failed to load {folder}.{filename}: {e}")


# -----------------------------
# BOT RUNNER
# -----------------------------
if __name__ == "__main__":
    async def main():
        await load_all_cogs()

        token = os.environ.get("DISCORD_TOKEN") or config.get("token")

        if not token:
            print("❌ ERROR: No bot token found in ENV or config.json")
            return
        
        await bot.start(token)

    import asyncio
    asyncio.run(main())
