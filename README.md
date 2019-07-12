# KTHack management system

*Heavily inspired by [HackUPC registration](https://github.com/hackupc/registration).*

## Project setup

Requirements: Python 3 and virtualenv.

- `git clone https://github.com/kthackais/mykthack && cd mykthack`.
- `virtualenv env --python=python3`.
- `source ./env/bin/activate`.
- `pip install -r requirements.txt`.

Continue with only one of the following sections depending on the purpose of the deploy.

### Local server

- `python manage.py migrate`.
- `python manage.py createsuperuser`.
- `python manage.py runserver`.

### Production server

- `cp server.sh.template server.sh`.
- Edit the `server.sh` file with the correct values of the environmental variables on each `[VARIABLE]`.
- `chmod +x server.sh`.
- `cp restart.sh.template restart.sh`.
- Edit the `restart.sh` file with the correct values of the environmental variables on each `[VARIABLE]`.
- `chmod +x restart.sh`.
- `./restart.sh`


## Environmental variables

- **SECRET_KEY**: Application secret (to generate one, run `os.urandom(24)`).
- **PROD_MODE**: Disable Django debug mode, should be `True` on production site.
- **PG_NAME**: PostgreSQL database name.
- **PG_USER**: PostgreSQL username.
- **PG_PWD**: PostgreSQL password.
- **PG_HOST**: PostgreSQL host (`'localhost'` by default).
- **SG_KEY**: SendGrid API key for email handling.
- **HK_DOMAIN**: Hackathon domain.