import discord
from discord import FFmpegPCMAudio
from discord.ext import commands 
from discord.channel import VoiceChannel
from discord.commands import Option, OptionChoice, SlashCommandGroup
import requests
import pydub
import os
import asyncio

intents = discord.Intents.default()
# 特権インテントを与える例
intents.message_content = True
bot = commands.AutoShardedBot(intents=intents)
TOKEN = os.getenv("TOKEN")

GUILD_IDS = [881524267601244220]

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond(content="BOT管理者限定コマンドです", ephemeral=True)
    else:
        raise error

@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f"新規導入サーバー: {guild.name}")

@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")

voiceChannel: VoiceChannel

@bot.slash_command(description="接続", guild_ids=GUILD_IDS)
async def join(ctx: discord.ApplicationContext):
    global voiceChannel
    voiceChannel = await ctx.author.voice.channel.connect()
    await ctx.response.send_message(content="接続しました。")
    play_voice("接続完了")

@bot.slash_command(description="退出", guild_ids=GUILD_IDS)
async def exit(ctx: discord.ApplicationContext):
    global voiceChannel
    play_voice("退出します")
    voiceChannel.stop()
    await voiceChannel.disconnect()
    await ctx.response.send_message(content="退出しました。")

@bot.event
async def on_message(message):
    global voiceChannel
    if message.author.bot:
        return
    play_voice(message.content)

def play_voice(text):
    global voiceChannel

    text = edit_text(text)

    response = requests.post(f"http://voicevox-engine:50021/audio_query?text={text}&speaker=1")
    response = requests.post("http://voicevox-engine:50021/synthesis?speaker=1", json=response.json())
    
    if response.status_code == 200:
        audio_data = response.content
        with open("out.wav", "wb") as f:
            f.write(audio_data)
        sound = pydub.AudioSegment.from_wav("out.wav")
        sound.export("out.mp3", format="mp3")
        voiceChannel.play(FFmpegPCMAudio("out.mp3"))
    else:
        print("Failed to generate voice")
        print(response.status_code)
        print(response.text)

def edit_text(text):
    text = text.replace(" ", "")
    text = text.replace("　", "")
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    if len(text) > 50:
        text = text[:50]+"以下省略"
    return text

bot.run(TOKEN)