import os

HACKATHON_NAME = 'KTHack'
HACKATHON_DESCRIPTION = 'Don\'t miss the oportunity to take part into Sweden\'s first student hackathon'
HACKATHON_TIMEZONE = 'Europe/Stockholm'
HACKATHON_DOMAIN = os.environ.get('HK_DOMAIN', 'localhost:8000')
HACKATHON_CONTACT_EMAIL = 'contact@kthack.com'
HACKATHON_ORGANIZER_EMAIL_REGEX = '^.*@kthack\.com$'
HACKATHON_WEBDEV_EMAIL = 'webdev@hackupc.com'

# TODO: Add the rest of variables including images, Google Analytics, social networks, texts, currency, deadlines...
