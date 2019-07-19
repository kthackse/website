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

HACKATHON_SN_FACEBOOK = "kthackais"
HACKATHON_SN_TWITTER = "kthackais"
HACKATHON_SN_INSTAGRAM = "kthackais"
HACKATHON_SN_YOUTUBE = "kthackais"
HACKATHON_SN_LINKEDIN = "kthackais"
HACKATHON_SN_MEDIUM = "kthackais"
HACKATHON_SN_GITHUB = "kthackais"

# TODO: Add the rest of variables including images, Google Analytics, texts, currency, deadlines...
