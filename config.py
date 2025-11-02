# config.py
import os

# 1. Telegram API Credentials
# IMPORTANT: Use environment variables in production!
TG_API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
TG_API_HASH = os.getenv('TELEGRAM_API_HASH', '')
TG_STRING_SESSION = os.getenv('TELEGRAM_STRING_SESSION', None)

# 1.b External News APIs
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
NEWSDATA_API_KEY = os.getenv('NEWSDATA_API_KEY', '')

# 1.c Gemini (Google Generative AI)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# 2. Trusted Telegram Channels
# Add the usernames of the public channels you want to use as your knowledge base.
# Examples are provided below. You can add or remove channels as needed.
# Make sure the bot/user account has access to these channels.
TRUSTED_CHANNELS = [
    # Updated per user request (Nov 1, 2025)
    "iraqfpg",
    # News & TV
    "alsumariatviraq",
    "alrabiaatv",
    "alsharqiyagroup",
    "fallujahtv",
    "UtvIraq",
    "Tech4peace",
    "inainaiq",
    "baghdadtoday",
    "IraqiPmo",
    "iraqi1_news",
    # Government & Ministries
    "ministry_of_oil",
    "Educationiq",
    "MODiraq",
    "molsa2023",
    "moiiraqi",
    "mohesr_official_channel",
    "BROTHERSIRQ",
]

# Removed - moved to environment variable above
# TG_STRING_SESSION = None
