import aiohttp
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.environ.get("TOKEN")
WEBHOOK=os.environ.get("WEBHOOK")
WEBHOOK2=os.environ.get("WEBHOOK2")
CHANNEL_10M=1430459323716337795
CHANNEL_100M=1430459403034955786
PHRASES=["Chipso and Queso","Los Primos","Eviledon","Los Tacoritas","Tang Tang Keletang","Ketupat Kepat","Tictac Sahur","La Supreme Combinasion","Ketchuru and Musturu","Garama and Madundung","Spaghetti Tualetti","Spooky and Pumpky","La Casa Boo","La Secret Combinasion","Burguro And Fryuro","Headless Horseman","Dragon Cannelloni","Meowl","Strawberry Elephant"]
async def validate_webhook(webhook_url, channel_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(webhook_url) as response:
                if response.status in (200, 204):
                    print(f"Webhook valid for channel {channel_id}")
                    return True
                else:
                    print(f"Invalid webhook for channel {channel_id}: Status {response.status}")
                    return False
        except Exception as e:
            print(f"Webhook validation error for channel {channel_id}: {e}")
            return False
async def make_request(session, url, headers, max_retries=5):
    retries=0
    base_delay=1
    while retries < max_retries:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 429:
                    retry_after=float(response.headers.get("Retry-After", base_delay))
                    print(f"Rate limited (429) for {url}. Waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    retries += 1
                    base_delay *= 2
                    continue
                elif response.status != 200:
                    print(f"API error for {url}: Status {response.status}")
                    return None
                return await response.json()
        except Exception as e:
            print(f"Request error for {url}: {e}")
            retries += 1
            await asyncio.sleep(base_delay)
            base_delay *= 2
    print(f"Max retries reached for {url}")
    return None
async def send_webhook(webhook_url, content, channel_id):
    async with aiohttp.ClientSession() as session:
        try:
            webhook_data={'content':content,'username':'Job ID Bot'}
            async with session.post(webhook_url, json=webhook_data) as response:
                if response.status != 204:
                    print(f"Failed to send webhook for channel {channel_id}: Status {response.status}")
        except Exception as e:
            print(f"Webhook send error for channel {channel_id}: {e}")
async def monitor_discord_channels():
    headers={'Authorization':TOKEN,'Content-Type':'application/json','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    if not await validate_webhook(WEBHOOK, CHANNEL_10M) or not await validate_webhook(WEBHOOK2, CHANNEL_100M):
        print("Aborting due to invalid webhook(s)")
        return
    async with aiohttp.ClientSession() as session:
        last_message_ids={str(CHANNEL_10M):None,str(CHANNEL_100M):None}
        for cid in [CHANNEL_10M,CHANNEL_100M]:
            url=f"https://discord.com/api/v9/channels/{cid}/messages?limit=1"
            messages=await make_request(session, url, headers)
            if messages is None:
                print(f"Failed to connect to channel {cid}")
                return
            last_message_ids[str(cid)]=messages[0]['id'] if messages else None
            print(f"Connected to channel {cid}. Last message: {last_message_ids[str(cid)]}")
        while True:
            for cid, webhook_url in [(CHANNEL_10M,WEBHOOK),(CHANNEL_100M,WEBHOOK2)]:
                try:
                    url=f"https://discord.com/api/v9/channels/{cid}/messages?after={last_message_ids[str(cid)]}&limit=10"
                    messages=await make_request(session, url, headers)
                    if messages:
                        for message in reversed(messages):
                            content=message['content']
                            if content:
                                for phrase in PHRASES:
                                    if phrase.lower() in content.lower():
                                        content=f"@everyone {content}"
                                        break
                                await send_webhook(webhook_url, content, cid)
                            last_message_ids[str(cid)]=message['id']
                    await asyncio.sleep(1)
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
