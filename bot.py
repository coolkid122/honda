import discord
import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.environ.get("TOKEN")
WEBHOOK=os.environ.get("WEBHOOK")
CHANNEL_IDS=[1430459403034955786,1430459323716337795]
PHRASES=["Chipso and Queso","Los Primos","Eviledon","Los Tacoritas","Tang Tang Keletang","Ketupat Kepat","Tictac Sahur","La Supreme Combinasion","Ketchuru and Musturu","Garama and Madundung","Spaghetti Tualetti","Spooky and Pumpky","La Casa Boo","La Secret Combinasion","Burguro And Fryuro","Headless Horseman","Dragon Cannelloni","Meowl","Strawberry Elephant"]
async def monitor_discord_channels():
    headers={'Authorization':TOKEN,'Content-Type':'application/json','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    async with aiohttp.ClientSession() as session:
        last_message_ids={str(cid):None for cid in CHANNEL_IDS}
        for cid in CHANNEL_IDS:
            url=f"https://discord.com/api/v9/channels/{cid}/messages?limit=1"
            try:
                async with session.get(url,headers=headers) as response:
                    if response.status==200:
                        messages=await response.json()
                        last_message_ids[str(cid)]=messages[0]['id'] if messages else None
                        print(f"Connected to channel {cid}. Last message: {last_message_ids[str(cid)]}")
                    else:
                        print(f"Error for channel {cid}: {response.status}")
                        return
            except Exception as e:
                print(f"Connection error for channel {cid}: {e}")
                return
        while True:
            for cid in CHANNEL_IDS:
                try:
                    url=f"https://discord.com/api/v9/channels/{cid}/messages?after={last_message_ids[str(cid)]}&limit=10"
                    async with session.get(url,headers=headers) as response:
                        if response.status==200:
                            messages=await response.json()
                            for message in reversed(messages):
                                for phrase in PHRASES:
                                    if phrase.lower() in message['content'].lower():
                                        async with aiohttp.ClientSession() as session:
                                            webhook_data={'content':message['content'],'username':'Job ID Bot'}
                                            async with session.post(WEBHOOK,json=webhook_data) as response:
                                                if response.status!=204:
                                                    print(f"Failed to send webhook: {response.status}")
                                        break
                                last_message_ids[str(cid)]=message['id']
                        else:
                            print(f"API error for channel {cid}: {response.status}")
                except Exception as e:
                    print(f"Polling error for channel {cid}: {e}")
async def main():
    if not TOKEN or not WEBHOOK:
        print("Missing TOKEN or WEBHOOK environment variables")
        return
    try:
        await monitor_discord_channels()
    except Exception as e:
        print(f"Error: {e}")
if __name__=="__main__":
    import asyncio
    asyncio.run(main())
