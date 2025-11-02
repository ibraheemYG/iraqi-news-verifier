# telegram_reader.py
import asyncio
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Channel
import datetime

# Import configuration from config.py
try:
    from config import TG_API_ID, TG_API_HASH, TRUSTED_CHANNELS, TG_STRING_SESSION
except ImportError:
    print("ERROR: config.py not found or variables are missing.")
    print("Please create a config.py file with TG_API_ID, TG_API_HASH, and TRUSTED_CHANNELS.")
    exit()

# Use a specific session name for this application
SESSION_NAME = "iraqi_news_verifier"
SESSION_DIR = Path("telegram_sessions")
SESSION_FILE = SESSION_DIR / f"{SESSION_NAME}.session"

async def fetch_from_channel(client, channel_username, limit):
    """Fetch up to `limit` text messages from a public channel with pagination."""
    channel_articles = []
    try:
        entity = await client.get_entity(channel_username)

        total_limit = max(1, int(limit))
        offset_id = 0
        fetched_total = 0
        while fetched_total < total_limit:
            batch_size = min(100, total_limit - fetched_total)
            msgs = await client.get_messages(entity, limit=batch_size, offset_id=offset_id)
            if not msgs:
                break

            for message in msgs:
                if message and getattr(message, "text", None):
                    url = f"https://t.me/{channel_username}/{message.id}"
                    parts = message.text.split('\n', 1)
                    title = parts[0]
                    body = parts[1] if len(parts) > 1 else title
                    channel_articles.append({
                        "title": title,
                        "body": body,
                        "url": url,
                        "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    })

            fetched = len(msgs)
            fetched_total += fetched
            offset_id = msgs[-1].id

        print(f"  - [OK] Fetched {len(channel_articles)} messages from {channel_username}")
        return channel_articles
    except ValueError:
        print(f"  - [ERROR] Channel '{channel_username}' not found or access denied.")
        return []
    except Exception as e:
        print(f"  - [ERROR] Unexpected error with {channel_username}: {e}")
        return []

async def get_telegram_messages(limit_per_channel=10):
    """Connects to Telegram and fetches recent messages from all trusted channels concurrently."""

    if TG_STRING_SESSION:
        client = TelegramClient(StringSession(TG_STRING_SESSION), TG_API_ID, TG_API_HASH)
    else:
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        client = TelegramClient(str(SESSION_FILE), TG_API_ID, TG_API_HASH)

    try:
        await client.start()
        print("Telegram client connected successfully.")

        print("Successfully connected to Telegram. Starting concurrent fetch...")

        tasks = [fetch_from_channel(client, username, limit_per_channel) for username in TRUSTED_CHANNELS]
        results = await asyncio.gather(*tasks)
        all_articles = [article for sublist in results for article in sublist]

        return all_articles
    
    except Exception as e:
        print(f"Error connecting to Telegram: {e}")
        return []
    
    finally:
        await client.disconnect()

# This allows running the file directly for testing purposes
if __name__ == "__main__":
    print("--- Running Telegram Reader Standalone Test ---")
    
    # Use asyncio.run() to execute the async function from a sync context
    fetched_articles = asyncio.run(get_telegram_messages(limit_per_channel=5))
    
    if fetched_articles:
        print(f"\n\nSuccessfully fetched a total of {len(fetched_articles)} articles.")
        # Print details of the first article for verification
        print("\nExample of first article fetched:")
        print(fetched_articles[0])
    else:
        print("\n\nNo articles were fetched. Please check your config.py and network connection.")
