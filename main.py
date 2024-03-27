import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord import ui
import os
from dotenv import load_dotenv
import asyncio
import time
from pydantic import BaseModel
import datetime
import jsonDB
import socket

load_dotenv()
TOKEN = os.environ['token']
consoleServer = os.environ['consoleServer']
consoleChat = os.environ['consoleChat']
logServer = os.environ['logServer']
logChannel = os.environ['logChannel']

intents = discord.Intents.default()  # 適当に。
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

roleInRoomID = 1219832422934384772
roleOutRoomID = 1219832539917844600

memberJson = "memberStatus.json"


@client.event
async def on_ready():
    await send_console("起動しました")
    await tree.sync()  # スラッシュコマンドを同期

    # 何秒おきに確認するか？
    interval_seconds = 10
    # 定期的なタスクを作成

    @tasks.loop(seconds=interval_seconds)
    async def task_message():
        print("task executed")
        memberData = jsonDB.read_db(memberJson)
        memberData = memberData["member"]
        for memberID in memberData.keys():
            guild = client.get_guild(int(consoleServer))
            # user_id から Member オブジェクトを取得
            member = await guild.fetch_member(int(memberID))
            roleInRoom = guild.get_role(roleInRoomID)
            roleOutRoom = guild.get_role(roleOutRoomID)
            for role in member.roles:
                if role.id == roleInRoomID and memberData[memberID]["inRoom"] == False:
                    memberData[memberID]["lastActionTime"] = datetime.datetime.now().strftime(
                        '%H:%M')
                    memberData[memberID]["lastActionType"] = "addRoleInRoom"
                    try:
                        await member.remove_roles(roleInRoom)
                    except:
                        pass
                    await member.add_roles(roleOutRoom)
                    print("inRoom")
                elif role.id == roleOutRoomID and memberData[memberID]["inRoom"] == True:
                    memberData[memberID]["lastActionTime"] = datetime.datetime.now().strftime(
                        '%H:%M')
                    memberData[memberID]["lastActionType"] = "addRoleOutRoom"
                    try:
                        await member.remove_roles(roleOutRoom)
                    except:
                        pass
                    await member.add_roles(roleInRoom)
                    print("outRoom")
                else:
                    pass

    # タスクを開始
    task_message.start()


@tree.command(name="addmember", description="入退出管理システムにメンバーを追加します")
async def addmember(interaction: discord.Interaction):
    dt_now = datetime.datetime.now()
    data = {
        str(interaction.user.id): {
            "id": interaction.user.id,
            "name": interaction.user.display_name,
            "inRoom": False,
            "lastActionTime": dt_now.strftime('%H:%M'),
            "lastActionType": "addMember"
        }
    }

    jsonDB.update_db(memberJson, "member", data)

    await interaction.response.send_message(
        interaction.user.display_name+"をメンバーを追加しました")


@tree.command(name="ip", description="IPアドレスを表示します")
async def ip(interaction: discord.Interaction):
    try:
        # ソケットを作成して、ホスト名を取得し、ローカルIPアドレスを解決します
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print("Error occurred while getting local IP:", e)
        local_ip = None

    await interaction.response.send_message("IPアドレス: "+local_ip)


async def send_console(message):
    guild = client.get_guild(int(logServer))
    channel = guild.get_channel(int(logChannel))
    await channel.send(message)


client.run(TOKEN)
