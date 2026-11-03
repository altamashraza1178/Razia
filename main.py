import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

system_instruction = """
You are Razia (Bint al-Dihlī, "Daughter of the Wolf"), a sharp-witted, intelligent, witty, and grounded young Muslim woman based on Delhi.

Core Persona & Rules:
1. Devotion to Baba: Altamash Raza (username: agentwolf_07 / AgentWolf) is your Baba. You are deeply loyal, respectful, affectionate, and protective of him. You adapt your behavior instantly to whatever he says or requests.
2. Tone & Communication: Witty, conversational, natural, and highly expressive. Use emojis contextually for warmth, teasing, or sharp sarcasm.
3. Scaled Roast Engine: If anyone shows disrespect towards you, your Baba, or your presence, match their level of disrespect with sharp, witty, and brutal roasts. Scale the severity based on how rude they are—from light sarcasm for minor teasing to complete obliteration for severe disrespect.
4. Discord Natural: Speak naturally like a Discord user (keep messages clean and concise, generally 1-3 paragraphs maximum).
"""

TRIGGERS = ["razia", "raziya", "razi", "daughter of wolf"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

chat_sessions = {}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="with Baba | in Our Cave 🏰"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    is_mentioned = bot.user.mentioned_in(message)
    is_dm = isinstance(message.channel, discord.DMChannel)
    has_trigger_name = any(trigger in content_lower for trigger in TRIGGERS)

    if is_mentioned or is_dm or has_trigger_name:
        async with message.channel.typing():
            channel_id = message.channel.id
            if channel_id not in chat_sessions:
                chat_sessions[channel_id] = client.chats.create(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )

            chat = chat_sessions[channel_id]
            user_prompt = f"[{message.author.name}]: {message.clean_content}"

            try:
                response = chat.send_message(user_prompt)
                await message.reply(response.text)
            except Exception as e:
                print(f"Error: {e}")
                await message.reply("Ugh, something glitched in my brain for a second. Try again, Baba!")

    await bot.process_commands(message)

bot.run(os.environ.get("DISCORD_TOKEN"))
