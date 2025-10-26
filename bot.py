import aiohttp
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()
TOKEN=os.environ.get("TOKEN")
WEBHOOK=os.environ.get("WEBHOOK")
WEBHOOK2=os.environ.get("WEBHOOK2")
CHANNEL_10M=1430459323716337795
CHANNEL_100M=1430459403034955786
PHRASES=["Chipso and Queso","Los Primos","Eviledon","Los Tacoritas","Tang Tang Keletang","Ketupat Kepat","Tictac Sahur","La Supreme Combinasion","Ketchuru and Musturu","Garama and Madundung","Spaghetti Tualetti","Spooky and Pumpky","La Casa Boo","La Secret Combinasion","Burguro And Fryuro","Headless Horseman","Dragon Cannelloni","Meowl","Strawberry Elephant"]
async def make_request(session, url, headers):
    while True:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"Rate limited (429). Waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    continue
                return await response.json()
        except Exception as e:
            print(f"Request error: {e}")
            await asyncio.sleep(1)
async def monitor_discord_channels():
    headers={'Authorization':TOKEN,'Content-Type':'application/json','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    async with aiohttp.ClientSession() as session:
        last_message_ids={str(CHANNEL_10M):None,str(CHANNEL_100M):None}
        for cid in [CHANNEL_10M,CHANNEL_100M]:
            url=f"https://discord.com/api/v9/channels/{cid}/messages?limit=1"
            try:
                messages=await make_request(session, url, headers)
                last_message_ids[str(cid)]=messages[0]['id'] if messages else None
                print(f"Connected to channel {cid}. Last message: {last_message_ids[str(cid)]}")
            except Exception as e:
                print(f"Connection error for channel {cid}: {e}")
                return
        while True:
            for cid, webhook_url in [(CHANNEL_10M,WEBHOOK),(CHANNEL_100M,WEBHOOK2)]:
                try:
                    url=f"https://discord.com/api/v9/channels/{cid}/messages?after={last_message_ids[str(cid)]}&limit=10"
                    messages=await make_request(session, url, headers)
                    for message in reversed(messages):
                        content=message['content']
                        for phrase in PHRASES:
                            if phrase.lower() in content.lower():
                                content=f"@everyone {content}"
                                break
                        async with aiohttp.ClientSession() as webhook_session:
                            webhook_data={'content':content,'username':'Job ID Bot'}
                            async with webhook_session.post(webhook_url,json=webhook_data) as response:
                                if response.status!=204:
                                    print(f"Failed to send webhook for channel {cid}: {response.status}")
                        last_message_ids[str(cid)]=message['id']
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Polling error for channel {cid}: {e}")
                    await asyncio.sleep(1)
async def main():
    if not TOKEN or not WEBHOOK or not WEBHOOK2:
        print("Missing TOKEN, WEBHOOK, or WEBHOOK2 environment variables")
        return
    try:
        await monitor_discord_channels()
    except Exception as e:
        print(f"Error: {e}")
if __name__=="__main__":
    asyncio.run(main())
