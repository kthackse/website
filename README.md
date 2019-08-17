# KTHack website

![Website preview](app/static/img/preview.png)

[![Maintainability](https://api.codeclimate.com/v1/badges/7f4f5aad1aea61832fae/maintainability)](https://codeclimate.com/github/kthackse/website/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/7f4f5aad1aea61832fae/test_coverage)](https://codeclimate.com/github/kthackse/website/test_coverage)
[![Build Status](https://travis-ci.com/kthackse/website.svg?branch=master)](https://travis-ci.com/kthackse/website)

:computer: Website and management system for KTHack, heavily inspired by [HackUPC registration](https://github.com/hackupc/registration)

:raising_hand: Current maintainer: [@oriolclosa](https://github.com/oriolclosa)

## Features

### Users

- User signup and login management, profile page including picture and basic information.
- Email verification and automatic emails.
- Organisational departments for organiser permissions management.
- Companies for sponsors and recruitment identification.
- Different user types, participant, organiser, volunteer, mentor, sponsor, recruiter and media. Organisers and volunteers can be assigned to departments, sponsors and recruiters can be linked with a company.
- All users can update their information via the profile page, a history of the changes is kept.

### Events

- Support for multievent management, however, only one event can be active at the same time.
- Schedule can be added and related to an event creating a live page with added information. Important events are also sent as a summary on the corresponding emails. Automatic schedule PDF creation.
- Event application created by registered users on the system.
- Team management among users, creation, joining and removal along with name setting.
- Application voting and comment for organisers.
- Dubious event application management.
- Reimbursement management.
- Invoice generation and automatic sending from SVG template.

### Jobs

- Job offers management related to companies which can be both internal or external linking it to the company's own recruitment tool.
- Job applications created by registered users on the system.

### Pages

- Page management, add static pages to the website setting the title and content.

## Project setup

Requirements: Python 3.6 or greater, Cairo graphics, virtualenv and pip.

- `git clone https://github.com/kthackse/website && cd website`.
- `virtualenv env --python=python3`.
- `source ./env/bin/activate`.
- `pip install -r requirements.txt`.

Continue with only one of the following sections depending on the purpose of the deploy.

### Local server

- `python manage.py migrate`.
- `python manage.py loaddata initial`.
- `python manage.py createsuperuser`.
- `python manage.py runserver`.

### Production server

Requirements: PostgreSQL, nginx and certbot.

#### PostgreSQL database

- `sudo -u postgres psql`.
- `CREATE DATABASE [DATABASE_NAME];`.
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

##### Autodeploy
- `cp deploy.sh.template deploy.sh`.
- Edit the `deploy.sh` file with the correct value for the service name.
- `chmod +x deploy.sh`.
- Add the following to `/etc/sudoers`.
```
[USER] cms051=/usr/bin/systemctl restart mykthack.service
```
- Replace `[USER]` with your username.

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

    server_name kthack.com www.kthack.com;
    
    proxy_set_header X-Real-IP $remote_addr;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    
    location /static/ {
        alias [PROJECT_FOLDER]/staticfiles/;
    }
    
    location /files/ {
        alias [PROJECT_FOLDER]/files/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:[PROJECT_FOLDER]/mykthack.sock;
        client_max_body_size 5M;
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

#### File template fonts

- Upload the fonts used in the SVGs to `~/.local/share/fonts/`.
- `fc-cache -f -v`.

#### Slack bot

- Create a Slack bot on `https://api.slack.com/apps/new`.
- Activate incoming webhooks and add a webhook URL to the `#webdev-activity` channel.
- Add the bot to your workspace.
- Set the client ID and secret in `server.sh`.

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
- **HK_IP**: Hackathon server IP.
- **SE_URL**: Sentry post URL.
- **SE_ENV**: Sentry environment.
- **GO_ID**: Google Analytics ID.
- **GH_KEY**: GitHub webhook key.
- **GH_BRANCH**: GitHub current branch, defaults to `master`.
- **SL_ID**: Slack app client ID.
- **SL_SECRET**: Slack app client secret.
- **SL_INURL**: Internal organisation Slack webhook URL for deployments.

## Management guide

### Events

You can add multiple events with different ranges of dates as only one can be active at a given time. Events are not published by default and need to be activated to do so. Appart from the name, code, location and dates, an application deadline as well as the current status of applications must be provided.

The **homepage will automatically update** depending on the events you have on the system. This will take into account both temporal and application status factors. In case no event has already been added, a stock page will be displayed. If there are no more future events, the last event homepage will be displayed with some information about it. This will also reflect application status, from announcing the opening date to displaying a button indicating applications are open, to inform that they have already been closed.

If you want to **set your own homepage** for the current active event, you can do so by enabling the "custom home" option. The system will display the `index.html` located in `app/templates/custom/[EVENT_CODE]/` in case it's found. This will enable to display custom homepages if desired made with other tools such as a JavaScript framework.

A live page with all the schedule will also be automatically created with the data provided as schedule events. These can also be marked as important (which will make them appear on the email summary) and don't necessarily need to have a end time.

### Pages

You can also add pages to the site, by default, `Terms & Conditions`, `Privacy and Cookies Policy` and `Legal Notice` pages are created with their own content. However, you can add as many as you want. The content can either be plain text, HTML code, markdown or a markdown URL. This last one will retrieve the content of the link and render it as if you had written the text in markdown on the admin page itself. You can use this to display on the website a HTML rendered page of a public markdown file hosted on GitHub for exemple, such as a readme.

## Contribution

Please, report any incidents or questions to webdev@kthack.com.

### Style guidelines

A specific coding style is desired to keep consistency, please use [Black](https://github.com/python/black) in all your commited files. Pull Requests are required to pass all tests including the Travis CI pipeline on the repository.

### Commit message

Write it as you want, you did the work, not me. However, "Fix wrong event application status due to a missing if" will always be better than "Applications fixed" (doesn't apply to first commits of the repository).
