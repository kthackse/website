import os

HACKATHON_APP_NAME = "MyKTHack"
HACKATHON_NAME = "KTHack"
HACKATHON_DESCRIPTION = (
    "Don't miss the oportunity to take part into Sweden's first student hackathon"
)
HACKATHON_TIMEZONE = "Europe/Stockholm"
HACKATHON_DOMAIN = os.environ.get("HK_DOMAIN", "localhost:8000")
HACKATHON_IP = os.environ.get("HK_IP", "localhost:8000")
HACKATHON_EMAIL_CONTACT = "contact@kthack.com"
HACKATHON_ORGANIZER_EMAIL_REGEX = "^.*@kthack\.com$"
HACKATHON_EMAIL_WEBDEV = "webdev@kthack.com"
HACKATHON_EMAIL_SPONSORSHIP = "sponsorship@kthack.com"
HACKATHON_EMAIL_NOREPLY = "noreply@kthack.com"

HACKATHON_SN_FACEBOOK = "kthackse"
HACKATHON_SN_TWITTER = "kthackse"
HACKATHON_SN_INSTAGRAM = "kthackse"
HACKATHON_SN_YOUTUBE = "UCkurltTEv8ak0nd84DMJ4lA"
HACKATHON_SN_LINKEDIN = "kthackse"
HACKATHON_SN_MEDIUM = "kthackse"
HACKATHON_SN_GITHUB = "kthackse"

HACKATHON_EMAIL_PREFIX = "[" + HACKATHON_NAME + "] "

HACKATHON_VOTE_PERSONAL = 0.8
HACKATHON_VOTE_TECHNICAL = 0.2

HACKATHON_LEGAL_NAME = "KTH AI Society"
HACKATHON_LEGAL_ORGANISATION_NAME = "Tekniska Högskolans Studentkår"
HACKATHON_LEGAL_ORGANISATION_NUMBER = "802518-7249"
HACKATHON_LEGAL_ORGANISATION_BANKGIRO = "557-9198"
HACKATHON_LEGAL_ADDRESS_1 = "Drottning Kristinas Väg 15-19"
HACKATHON_LEGAL_ADDRESS_2 = ""
HACKATHON_LEGAL_POSTCODE = "100 44"
HACKATHON_LEGAL_CITY = "Stockholm"

# TODO: Add the rest of variables including images, Google Analytics, texts, currency, deadlines...
