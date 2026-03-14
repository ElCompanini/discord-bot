import discord
from discord.ext import commands
import requests
import os
import re
import yt_dlp
import asyncio


# Reemplaza el config.py por esto
TOKEN = os.getenv("TOKEN")
DEEPL_KEY = os.getenv("DEEPL_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='/', intents=intents)


#Opciones de YT

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'cookiefile': '/app/cookies.txt',
    'extractor_args': {'youtube': {'player_client': ['ios']}},
}

FFMPEG_OPTIONS = {'options': '-vn'}
queue = []

@bot.command()
async def play(ctx, *, search):
    #Verificar si hay alguien en el canal de voz
    if not ctx.author.voice:
        await ctx.send("No hay nadie en el canal de voz", delete_after=10)
        return
    
    voice_channel = ctx.author.voice.channel

    #Conectar al canal si hay alguien en él

    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    # Buscar en YT

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
        url = info['entries'][0]['title']
        title = info['entries'][0]['title']
    
    queue.append((url, title))
    await ctx.send(f"Agregada a la cola: **{title}**")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    if queue:
        url, title = queue.pop(0)
        souce = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        ctx.voice_client.play(souce, ater=lambda e: asyncio.run_coroutine_threadsafe)
        await ctx.send(f"Reproduciendo: **{title}**")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send(f"Cancion skipeada")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("Bot desconectado")

@bot.command()
async def cola(ctx):
    if not queue:
        await ctx.send("La cola está vacía")
    else:
        lista = "\n".join([f"{i+1}. {title}" for i, (_, title) in enumerate(queue)])
        await ctx.send(f"**Cola:**\n{lista}")

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

    # Agarrar mensaje del canal y no del caché

    channel = reaction.message.channel
    message = await channel.fetch_message(reaction.message.id)

    # No traducir si el mensaje está vacío
    if not message.content:
        await channel.send("❌ No text to translate.", delete_after=5)
        return

    translated = translate_text(message.content, target_lang)

    if translated is None:
        await channel.send("❌ Error translating.", delete_after=5)
        return

    # Enviar traducción y autoeliminarse a los 30 segundos
    await channel.send(
        f" **Translating to {emoji} ({target_lang}):**\n{translated}\n-# translated by {user.mention} • Deleting in 30s",
        delete_after=30
    )

bot.run(os.getenv("TOKEN"))