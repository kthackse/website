# KTHack management system

*Heavily inspired by [HackUPC registration](https://github.com/hackupc/registration).*

## Environmental variables
- **SECRET_KEY**: Application secret (to generate one, run `os.urandom(24)`).
- **PROD_MODE**: Disable Django debug mode, should be `True` on production site.
- **PG_NAME**: PostgreSQL database name.
- **PG_USER**: PostgreSQL username.
- **PG_PWD**: PostgreSQL password.
- **PG_HOST**: PostgreSQL host (`'localhost'` by default).
- **SG_KEY**: SendGrid API key for email handling.
- **HK_DOMAIN**: Hackathon domain.