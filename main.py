import discord 
from discord.ext import commands
import os
import json

# -----------------------------
# DISABLE ALL VOICE FEATURES
# -----------------------------
import discord.voice_client
discord.voice_client.has_nacl = lambda: False


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG_PATH = "config.json"
if not os.path.exists(CONFIG_PATH):
    raise SystemExit("config.json not found. Fill it with your bot token and settings.")
config = load_json(CONFIG_PATH)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, application_id=config.get("application_id"))

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        await bot.tree.sync()
        print("✔ Slash commands synced globally.")
    except Exception as e:
        print("❌ Failed to sync commands:", e)

async def load_all_cogs():
    # load only python files in cogs (ignore __init__.py)
    if os.path.exists("cogs"):
        for fn in os.listdir("cogs"):
            if fn.endswith(".py") and not fn.startswith("__"):
                try:
                    await bot.load_extension(f"cogs.{fn[:-3]}")
                    print(f"Loaded cog: cogs/{fn}")
                except Exception as e:
                    print(f"Failed to load cog cogs/{fn}: {e}")

    # ensure utils exist but do not load as cogs
    if not os.path.exists("utils"):
        os.makedirs("utils", exist_ok=True)

    # create data folder for ticket_config
    if not os.path.exists("data"):
        os.makedirs("data", exist_ok=True)

async def main():
    await load_all_cogs()
    token = os.environ.get("DISCORD_TOKEN") or config.get("token")
    if not token:
        print("❌ No DISCORD_TOKEN env var and no token in config.json")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
