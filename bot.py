import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask, request, jsonify
import threading
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.getenv("TOKEN")
WEBHOOK=os.getenv("WEBHOOK")
CHANNEL_IDS=[123456789012345678,987654321098765432]
PORT=int(os.getenv("PORT",8080))
PHRASES=["Chipso and Queso","Los Primos","Eviledon","Los Tacoritas","Tang Tang Keletang","Ketupat Kepat","Tictac Sahur","La Supreme Combinasion","Ketchuru and Musturu","Garama and Madundung","Spaghetti Tualetti","Spooky and Pumpky","La Casa Boo","La Secret Combinasion","Burguro And Fryuro","Headless Horseman","Dragon Cannelloni","Meowl","Strawberry Elephant"]
intents=discord.Intents.default()
intents.message_content=True
bot=commands.Bot(command_prefix="!",intents=intents)
job_ids={"job_ids10m":"No job ID available","job_ids100m":"No job ID available"}
app=Flask(__name__)
@app.route("/pets",methods=["GET"])
async def pets():
    user_agent=request.headers.get("User-Agent")
    if not user_agent or "Roblox/WinInet" not in user_agent:
        return jsonify({"error":"Access Denied: Only Roblox requests allowed"}),403
    return jsonify(job_ids)
@bot.event
async def on_message(message):
    if message.channel.id in CHANNEL_IDS:
        for phrase in PHRASES:
            if phrase.lower() in message.content.lower():
                async with aiohttp.ClientSession() as session:
                    webhook_data={"content":f"New message in {message.channel.name}: {message.content}","username":"Job ID Bot"}
                    async with session.post(WHOOK,json=webhook_data) as response:
                        if response.status!=204:
                            print(f"Failed to send webhook: {response.status}")
                global job_ids
                job_ids["job_ids10m"]=f"{phrase}_10m_{message.id}"
                job_ids["job_ids100m"]=f"{phrase}_100m_{message.id}"
                break
    await bot.process_commands(message)
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
def run_flask():
    app.run(host="0.0.0.0",port=PORT)
if __name__=="__main__":
    flask_thread=threading.Thread(target=run_flask)
    flask_thread.start()
    bot.run(TOKEN)
