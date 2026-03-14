import discord
from discord.ext import commands
import requests
import os
import re


# Reemplaza el config.py por esto
TOKEN = os.getenv("TOKEN")
DEEPL_KEY = os.getenv("DEEPL_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.event
async def on_ready():
    print(f"Estamos dentro! {bot.user}")

FLAG_TO_LANG = {
    "🇺🇸": "EN-US",
    "🇬🇧": "EN-GB",
    "🇪🇸": "ES",
    "🇫🇷": "FR",
    "🇩🇪": "DE",
    "🇮🇹": "IT",
    "🇵🇹": "PT-PT",
    "🇧🇷": "PT-BR",
    "🇯🇵": "JA",
    "🇰🇷": "KO",
    "🇨🇳": "ZH",
    "🇷🇺": "RU",
    "🇳🇱": "NL",
    "🇵🇱": "PL",
    "🇸🇦": "AR",
}

def translate_text(text, target_lang):
    url = "https://api-free.deepl.com/v2/translate"  # Si tienes plan de pago: api.deepl.com
    headers = {
        "Authorization": f"DeepL-Auth-Key {os.getenv('DEEPL_KEY')}"
    }
    data = {
        "text": [text],
        "target_lang": target_lang
    }
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()["translations"][0]["text"]
    else:
        return None

@bot.event
async def on_ready():
    print(f"Corriendo el bot {bot.user}")

@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == bot.user:
        return

    if re.search(r'n *i *e *b *a|a *b *e *i *n', message.content.lower()):
        await message.channel.send("Based")

    # Necesario para que los demás comandos sigan funcionando
    await bot.process_commands(message)
@bot.event
async def on_reaction_add(reaction, user):
    # Ignorar reacciones del propio bot
    if user == bot.user:
        return

    emoji = str(reaction.emoji)

    # Verificar si el emoji es una bandera válida
    if emoji not in FLAG_TO_LANG:
        return

    target_lang = FLAG_TO_LANG[emoji]
    original_message = reaction.message

    # No traducir si el mensaje está vacío
    if not original_message.content:
        await original_message.channel.send("❌ No text to translate.", delete_after=5)
        return

    translated = translate_text(original_message.content, target_lang)

    if translated is None:
        await original_message.channel.send("❌ Error translating.", delete_after=5)
        return

    # Enviar traducción y autoeliminarse a los 30 segundos
    await original_message.channel.send(
        f" **Translating to {emoji} ({target_lang}):**\n{translated}\n-# translated by {user.mention} • Deleting in 30s",
        delete_after=30
    )

bot.run(os.getenv("TOKEN"))