import random
import asyncio

from discord import FFmpegOpusAudio, Member
from discord.ext import commands
from discord.utils import get, find
from youtube_dl import YoutubeDL
from queue import Queue

with open('secret') as f: 
    TOKEN = f.readline()
    GUILD = f.readline()

bot = commands.Bot(command_prefix='!')
q = Queue()


@bot.event
async def on_ready():
    print( f'{bot.user.name} has connected to Discord on server!\nCurrently connected to: ')
    async for guild in bot.fetch_guilds():
        print('- '+guild.name)

@bot.command(name='dado', help = 'Simula um dado rolando.')
async def roll(ctx, number_of_sides: int):
    dice = str(random.choice(range(1,number_of_sides+1)))
    await ctx.send(dice)

# sera q foi
# acho q n foi
@commands.has_role(888477749579218955)
@bot.command(name='clear')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

#music

@bot.command(name='play')
async def play(ctx, query,):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    voice = get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel
    guild = ctx.guild
    URL = {}

    # checar se usuario está em um canal
    if voice and voice.is_connected():
        if voice.is_playing():
            if voice.channel != channel:
                await ctx.send(f'O bot já está tocando no canal de voz {voice.channel}.')
                return
        else:
            await voice.move_to(channel)
    else:
        voice = await channel.connect()
    
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(query, download=False)

    URL['url'] = info['url']
    URL['duration']=info['duration']
    URL['title']=info['title']

    q.put(URL)
    
    if(voice.is_playing()):
        await ctx.send('_{}_ foi adicionada a fila.'.format(URL['title']))
        return
    else:
        await start_playing(ctx, voice, guild)


async def start_playing(ctx, voice, guild):
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    while(not q.empty()):
        info = q.get()
        voice.play(FFmpegOpusAudio(info['url'], **FFMPEG_OPTIONS))
        await ctx.send('Tocando agora:_ {} _'.format(info['title']))
        await asyncio.sleep(info['duration'])

# pause, play, resume, stop
@bot.command(name='queue')
async def print_queue(ctx):

    full_queue=''
    for count in range(len(q.queue)):
        count+1
        full_queue += '{} - {}\n'.format(count+1, q.queue[count]['title'])
    await ctx.send(f'```{full_queue}```')




@bot.command()
async def checkChannel(ctx, voice):
    channel = ctx.message.author.voice.channel
    if channel != voice.channel:
        await ctx.send('O bot já está sendo utilizado em outro canal.')
        return True
    else:
        return False

@bot.command(name='pause')
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    
    if await checkChannel(ctx, voice):
        return
    
    if voice.is_playing():
        voice.pause()
        await ctx.send('Pausando música.')

@bot.command(name='resume')
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if await checkChannel(ctx, voice):
        return

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Retornando música.')

@bot.command(name='stop', help='Para de tocar a musica e limpa toda a fila de músicas.')
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if await checkChannel(ctx, voice):
        return
    
    if voice.is_playing():
        voice.stop()
        await ctx.send('Parando a música e limpando a fila.')

@bot.command(name='disconnect')
async def disconnect(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel

    if await checkChannel(ctx, voice):
        return
    if voice:
        await voice.disconnect()
        await ctx.send('Até mais!')
    else:
        await ctx.send('O bot não está conectado em nenhum canal.')    

bot.run(TOKEN)