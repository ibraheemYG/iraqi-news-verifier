# config.py

# 1. Telegram API Credentials
# IMPORTANT: Keep this file secret. Do not share it publicly.
TG_API_ID = 21280170
TG_API_HASH = 'fb5d301280108b2229349120c3708c97'

# 1.b External News APIs (keep secret)
# NewsAPI.org API Key
NEWSAPI_KEY = 'f1d489d1c0e8475bb3653d4e6e629acb'
# NewsData.io API Key
NEWSDATA_API_KEY = 'pub_98f0b45800be407c8673160f32e51949'

# 1.c Gemini (Google Generative AI)
# Prefer reading from env GEMINI_API_KEY in production; kept here as per user request
GEMINI_API_KEY = 'AIzaSyBSBQ3nIkvlu-Ebix0P_uEpdUT-76HTfI0'

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

# Optional: if you generate a Telethon string session, put it here to skip manual login prompts
TG_STRING_SESSION = None
