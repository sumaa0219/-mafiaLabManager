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
import doorFunc
import csv
import datetime

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
lotDeviceJson = "lotDevice.json"


global defaultMAC


class InputMAC(ui.Modal):
    def __init__(self):
        super().__init__(
            title="起動したいパソコンのMACアドレスを入力してください",
        )
        self.uid = discord.ui.TextInput(
            label="MACアドレス",
            default=defaultMAC,
        )
        self.add_item(self.uid)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        global defaultMAC
        defaultMAC = defaultMAC.replace("-", ":")
        with open("user_MAC_data.csv", "r") as f:
            reader = csv.reader(f)
            User_MAC_Data = list(reader)

        wronFlag = 0
        for i, x in enumerate(User_MAC_Data):
            if x[0] == interaction.user.id:  # ID同じ場合
                if int(x[1]) == int(self.uid.value):  # 同じかつUIDが同じ場合
                    pass
                elif int(x[1]) is not int(self.uid.value):  # UIDだけ違う場合
                    User_MAC_Data[i][1] = int(self.uid.value)
                    with open("./user_MAC_data.csv", "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(User_MAC_Data)
            else:  # IDが違う
                wronFlag += 1

        if wronFlag == len(User_MAC_Data):
            new = [int(interaction.user.id), int(self.uid.value), None]
            User_MAC_Data.append(new)
            await send_console(User_MAC_Data)

            with open("./user_MAC_data.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(User_MAC_Data)

        await interaction.response.send_message(f"指定されたPCを起動しました{defaultMAC}")


@client.event
async def on_ready():
    await send_console("起動しました")
    await tree.sync()  # スラッシュコマンドを同期

    # 何秒おきに確認するか？
    interval_seconds = 10
    # 定期的なタスクを作成

    @tasks.loop(seconds=interval_seconds)
    async def task_message():
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


@tree.command(name="wol", description="PCを起動します")
async def wakeonlan(interaction: discord.Interaction):
    global defaultMAC
    with open('user_MAC_data.csv', 'r') as f:
        reader = csv.reader(f)
        data_list = list(reader)

    for i in data_list:
        if i[0] == interaction.user.id:
            defaultMAC = i[1]

    # modal = InputMAC()
    # await interaction.response.send_modal(modal)
    await interaction.response.send_message("指定されたPCを起動しました")


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


@tree.command(name="restart", description="再起動します")
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("再起動しました")
    os.system("sudo systemctl restart discordbot.service")


@tree.command(name="inroom", description="ステータスを入室に変更します")
async def inroom(interaction: discord.Interaction):
    memberData = jsonDB.read_db(memberJson)
    memberData = memberData["member"]
    memberData[str(interaction.user.id)]["inRoom"] = True
    jsonDB.update_db(memberJson, "member", memberData)
    username = interaction.user.display_name

    await interaction.response.send_message(f"{username}を入室にしました")


@tree.command(name="outroom", description="ステータスを退室に変更します")
async def outroom(interaction: discord.Interaction):
    memberData = jsonDB.read_db(memberJson)
    memberData = memberData["member"]
    memberData[str(interaction.user.id)]["inRoom"] = False
    jsonDB.update_db(memberJson, "member", memberData)
    username = interaction.user.display_name

    await interaction.response.send_message(f"{username}を退出にしました")


@tree.command(name="open", description="ドアを開けます")
async def open(interaction: discord.Interaction):
    data = jsonDB.read_db(lotDeviceJson)
    print(data["device"]["doorlock"]["status"])
    if data["device"]["doorlock"]["status"] == True:
        await interaction.response.send_message("ドアはすでに開いています")
        return
    else:
        await interaction.response.send_message("ドアを開けました")
        doorFunc.open()


@tree.command(name="close", description="ドアを閉めます")
async def close(interaction: discord.Interaction):
    data = jsonDB.read_db(lotDeviceJson)
    print(data["device"]["doorlock"]["status"])
    if data["device"]["doorlock"]["status"] == False:
        await interaction.response.send_message("ドアはすでに閉まっています")
        return
    else:
        await interaction.response.send_message("ドアを閉めました")
        doorFunc.close()


@tree.command(name="reserve", description="施設使用願を作成します")
async def reserve(interaction: discord.Interaction, times):
    await interaction.defer()
    today = datetime.datetime.now()
    weekList = []
    for count in times:
        weekList.append(today + datetime.timedelta(days=7*count))
    print(weekList)
    await interaction.followup.send("施設使用願を作成しました")


async def send_console(message):
    guild = client.get_guild(int(logServer))
    channel = guild.get_channel(int(logChannel))
    await channel.send(message)


client.run(TOKEN)
