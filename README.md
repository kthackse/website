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

Requirements: PostgreSQL, nginx and certbot.

#### PostgreSQL database

- `sudo -u postgres psql`.
- `CREATE DATABASE [DATABASE_NAME]`.
- `CREATE USER [DATABASE_USER] WITH PASSWORD '[DATABASE_PASSWORD]';`.
- Alter the created username for Django use.
```
ALTER ROLE [DATABASE_USER] SET client_encoding TO 'utf8';
ALTER ROLE [DATABASE_USER] SET default_transaction_isolation TO 'read committed';
ALTER ROLE [DATABASE_USER] SET timezone TO 'UTC';
```
- `GRANT ALL PRIVILEGES ON DATABASE [DATABASE_NAME] TO [DATABASE_USER];`.

#### Script files

- `cp server.sh.template server.sh`.
- Edit the `server.sh` file with the correct values of the environmental variables on each `[VARIABLE]`.
- `chmod +x server.sh`.
- `cp restart.sh.template restart.sh`.
- Edit the `restart.sh` file with the correct values of the environmental variables on each `[VARIABLE]`.
- `chmod +x restart.sh`.
- `./restart.sh`.

#### Gunicorn server

- `sudo vim /etc/systemd/system/mykthack.service`.
- Add the following content.
```
[Unit]
Description=MyKTHack daemon
After=network.target

[Service]
User=[USER]
Group=www-data
WorkingDirectory=[PROJECT_FOLDER]
ExecStart=[PROJECT_FOLDER]/server.sh >>[PROJECT_FOLDER]/out.log 2>>[PROJECT_FOLDER]/error.log

[Install]
WantedBy=multi-user.target
```
- Replace `[USER]` and `[PROJECT_FOLDER]` with your username and the full project location.
- `sudo systemctl start mykthack && sudo systemctl enable mykthack`.

#### Nginx server

- `sudo vim /etc/nginx/sites-available/kthack.com`.
- Add the following content.
```
server {
    listen 80;
    listen [::]:80;

    server_name kthack.com;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    
    location /static/ {
        alias /home/user/project_folder/staticfiles/;
    }
    
    location /files/ {
        alias /home/user/project_folder/files/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:[PROJECT_FOLDER]/mykthack.sock;
        client_max_body_size 5MB;
    }
}
```
- Replace `[PROJECT_FOLDER]` with the full project location.
- `sudo ln -s /etc/nginx/sites-available/kthack.com /etc/nginx/sites-enabled/`.
- `sudo nginx -t`.
- `sudo nginx -s reload`.
- A restart of the service could be needed if nginx has recently been installed which can be done by `sudo systemctl restart nginx`.

#### HTTPS certificates

- `sudo certbot --nginx -d kthack.com -d www.kthack.com`.
- Enter `2` if requested to redirect all HTTP traffic to HTTPS (rediction of all traffic to port `80` to `443`), this will also modify the previous nginx server configuration.
- `sudo nginx -s reload`.

## Project update

### Local server

The local server updates automatically once a change has been spotted, there's no need to do anything else.

### Production server

- `git pull`.
- `./restart.sh`.
- `sudo service mykthack restart`.

## Environmental variables

- **SECRET_KEY**: Application secret (to generate one, run `os.urandom(24)`).
- **PROD_MODE**: Disable Django debug mode, should be `True` on production site.
- **PG_NAME**: PostgreSQL database name.
- **PG_USER**: PostgreSQL username.
- **PG_PWD**: PostgreSQL password.
- **PG_HOST**: PostgreSQL host (`'localhost'` by default).
- **SG_KEY**: SendGrid API key for email handling.
- **HK_DOMAIN**: Hackathon domain.