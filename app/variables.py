import os

HACKATHON_APP_NAME = "MyKTHack"
HACKATHON_NAME = "KTHack"
HACKATHON_DESCRIPTION = (
    "Don't miss the oportunity to take part into Sweden's first student hackathon"
)
HACKATHON_TIMEZONE = "Europe/Stockholm"
HACKATHON_DOMAIN = os.environ.get("HK_DOMAIN", "localhost:8000")
HACKATHON_EMAIL_CONTACT = "contact@kthack.com"
HACKATHON_ORGANIZER_EMAIL_REGEX = "^.*@kthack\.com$"
HACKATHON_EMAIL_WEBDEV = "webdev@hackupc.com"

# TODO: Add the rest of variables including images, Google Analytics, social networks, texts, currency, deadlines...
