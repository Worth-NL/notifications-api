# Instructions for Notifications-api

This file contains all the instructions required to run the `api` locally. In addition, it lists all the changes made/settings applied to get the `Sandbox` environment running.

## Prerequisites

* Docker Desktop ([instructions for Mac](https://docs.docker.com/desktop/install/mac-install/))
* PostgreSQL 11 (for Mac, run in a terminal `$ brew install postgresql@11`)
* pgAdmin4 ([link for Mac](https://www.pgadmin.org/download/pgadmin-4-macos/))
* AWS CLI (for Mac, run in a terminal `$ brew install awscli`)
* Python 3.9 (if you want/need to run the api not in Docker)

## AWS configuration

Current implementation of the notifications app makes use of several AWS resources. These were created in an AWS account which belongs to Ernout.

The following resources were created:

* SES
* S3 buckets

If a new sandbox (non-production) AWS SES is to be setup, the following is most likely necessary:
> "You need to set up the email address you want to mail to in amazon - I don't know why. So I authorized emailing to my email address through amazon's web ui." - Ernout

For application to be able to communicate with AWS APIs, it needs API keys. Ask your fellow teammates for the keys and do the following:

1. In the home directory create `.aws` folder.
1. In `~/.aws/` create file “credentials” (no extension)
1. Place the following two rows in the file
```
aws_access_key_id=<KEY_ID_YOU_GOT>
aws_secret_access_key=<ACCESS_KEY_YOU_GOT>
```

## Database configuration

`Api` needs PostgreSQL database to store its data. In order to get it work locally, follow these steps:

1. Open a terminal window
1. Start the PostgreSQL server by running `$ /usr/local/opt/postgresql@11/bin/postgres -D /usr/local/var/postgresql@11`. This will run the service in the current terminal.
1. Open another terminal window and connect to the server with `$ psql --host=127.0.0.1 --port=5432 --dbname=postgres`
1. Once in the `psql` shell, run the following command to create a database called “notify” `$ create database notify;`
1. Start `pgAdmin` and connect to the database

The following changes must be made to the database:

| Table  | Column  | Row  | New value  | Comment  |
|---|---|---|---|---|
| `services`  | `email_from`  |   | `noreply`  | necessary for emails sending. `noreply` is the part of email address before `@`  |
| `domain`  | `domain`  |  | `worth.systems`  | if you want to create account using `worth.systems` email address. For `organisation_id` use an existing one in `organisation` table or create a new organisation  |
| `provider_details`  | `support_international`  | `Firetext`  | `true`  | necessary for sms sending  |
| `provider_details`  | `active` | `mmg` | `false` | necessary for sms sending |
| `service_sms_senders` | `sms_sender` | all rows | `NotifyNL` | necessary for sms sending. This one is important not to miss. If `GOVUK` is used as `sms_sender`, app will get blocked from being able to send sms |

## Running app

Follow the following steps to get the `Api` running locally in a Docker container:

1. Start Docker Desktop (Docker needs to be running)
1. Start PostgreSQL 11
1. Ask your fellow teammates for `FIRETEXT_API_KEY` and `FIRETEXT_INTERNATIONAL_API_KEY`
1. In the root of the repo create `environment.sh` with the following content
```
export NOTIFY_ENVIRONMENT='development'

export SQLALCHEMY_DATABASE_URI='postgresql://postgres:postgres@host.docker.internal/notify'

export MMG_API_KEY='MMG_API_KEY'
export FIRETEXT_API_KEY='<API_KEY_YOU_GOT>'
export FIRETEXT_INTERNATIONAL_API_KEY='<INTERNATIONAL_API_KEY_YOU_GOT>'
export NOTIFICATION_QUEUE_PREFIX='YOUR_OWN_PREFIX'

export FLASK_APP=application.py
export FLASK_DEBUG=1
export WERKZEUG_DEBUG_PIN=off

export APPLICATIONINSIGHTS_ENABLED=1
export APPLICATIONINSIGHTS_CONNECTION_STRING=<InstrumentationKey>
```
1. Ask your team for correct `<InstrumentationKey>`
1. Open a terminal in the root of the repo and run `$ make bootstrap-with-docker` to create the docker image
1. Run `$ make run-migrations-with-docker` to run migrations for the database
1. Run `$ make run-flask-with-docker`
1. Open another terminal and run `$ make run-celery-with-docker`. This worker will handle the notifications
1. The `api` is now available at `localhost:6011`


## Troubleshooting

### `$ make run-migrations-with-docker` fails with Error 1

Make sure you added AWS credentials. See [AWS configuration](#aws-configuration)

### `too many verify codes created` error

Empty the `verify_code` table in the database.