import discord
from discord.ext import commands
import requests
import os
import re
import asyncio
import wavelink

# Reemplaza el config.py por esto
TOKEN = os.getenv("TOKEN")
DEEPL_KEY = os.getenv("DEEPL_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='/', intents=intents)


#WaveLink


#Opciones de YT

@bot.event
async def on_ready():
    print(f"Estamos dentro! {bot.user}")
    try:
        node = await wavelink.NodePool.create_node(
            bot=bot,
            host='mainline.proxy.rlwy.net',
            port=25904,
            password='brooks80',
            https=False
        )
        print(f"Nodo conectado: {node.identifier}")
    except Exception as e:
        print(f"Error conectando nodo: {e}")

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"Nodo {node.identifier} conectado!")

@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice:
        await ctx.send("❌ Tienes que estar en un canal de voz.", delete_after=10)
        return

    vc: wavelink.Player = ctx.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)

    track = await wavelink.YouTubeTrack.search(search, return_first=True)
    if not track:
        await ctx.send("❌ No se encontró la canción.")
        return

    if vc.is_playing():
        await vc.queue.put_wait(track)
        await ctx.send(f"✅ Agregado a la cola: **{track.title}**")
    else:
        await vc.play(track)
        await ctx.send(f"🎵 Reproduciendo: **{track.title}**")

@bot.command()
async def skip(ctx):
    vc: wavelink.Player = ctx.voice_client
    if vc and vc.is_playing():
        await vc.stop()
        await ctx.send("⏭️ Canción saltada.")

@bot.command()
async def stop(ctx):
    vc: wavelink.Player = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send("⏹️ Bot desconectado.")

@bot.command()
async def cola(ctx):
    vc: wavelink.Player = ctx.voice_client
    if not vc or vc.queue.is_empty:
        await ctx.send("📭 La cola está vacía.")
    else:
        lista = "\n".join([f"{i+1}. {t.title}" for i, t in enumerate(vc.queue)])
        await ctx.send(f"🎵 **Cola:**\n{lista}")

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.event

@bot.event
async def on_ready():
    print(f"Estamos dentro! {bot.user}")
    await wavelink.NodePool.create_node(
        bot=bot,
        host='lavalink.api.seraphinachannel.com',
        port=443,
        password='HarukaAya!1',
        https=True
    )

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

    if re.search(r'b *a *s *e *d|d *e *s *a *b', message.content.lower()):
        await message.channel.send("Nieba")

    if re.search(r'd *a *r *i *c *k|k *c *i *r *a *d', message.content.lower()):
        await message.channel.send("God, that guy love cherry jam")

    if re.search(r'c *h *e *r *r *y|y *r *r *e *h *c', message.content.lower()):
        await message.channel.send("I know a guy who loves that jam")

    if re.search(r's *h *a *e|e *a *h *s', message.content.lower()):
        await message.channel.send("")

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