# Flask-CronDecorator

Securely decorates Google Cloud Cron Endpoints via convention and `X-Appengine-Cron` header.

Per [the docs](https://cloud.google.com/appengine/docs/flexible/python/scheduling-jobs-with-cron-yaml#validating_cron_requests):

>The X-Appengine-Cron header is set internally by Google App Engine. If your request handler finds this header it can trust that the request is a cron request. The X- headers are stripped by App Engine when they originate from external sources so that you can trust this header.

## Installation

Add this line to your application's requirements.txt

```python
Flask-CronDecorator
```

And then execute:

    $ pip install -r requirements.txt

Or install it yourself as:

    $ pip install Flask-CronDecorator

## Usage

The following snippet should get you coding
```python
from flask import Flask, Blueprint
from CronDecorator import CronDecorator
import logging
from datetime import datetime, timedelta
from models import Task, TaskRequest


app = Flask(__name__)
app.cron = CronDecorator(app)

# blueprint can optionally be passed in for registering cron task endpoints in a blueprint
admin = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')
blueprint.cron = CronDecorator(app, blueprint)

app.register_blueprint(admin)
_logger = logging.getLogger(__name__)


@admin.cron.task('/purge_tasks', methods=['GET'])  # creates /cron/admin/purge_tasks endpoint
def purge_tasks():
    _logger.info('Purging first 100 Tasks older than 1 year')
    year_ago = datetime.utcnow() - timedelta(days=365)
    tasks = Task.query.filter(Task.created <= year_ago).order_by(Task.id.asc()).limit(100).all()
    for task in tasks:
        db.session.delete(task)

    _logger.info('Purging first 1000 TaskRequests older than 2 weeks')
    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    task_requests = TaskRequest.query.join(Task).filter(
        models.Task.created <= two_weeks_ago
    ).order_by(Task.id.desc()).limit(1000).all()

    for task_request in task_requests:
        db.session.delete(task_request)

    db.session.commit()

    return '', 200
```

## Google Cloud Settings

Given the above snippet, you'll need to update your Google Cloud cron.yaml

```yaml
cron:
- description: "Purges Tasks older than 1 year and TaskRequests older than 2 weeks"
  url: /cron/admin/purge_tasks
  schedule: every 30 minutes
```

Be sure your /cron/* endpoints are covered in Google Cloud app.yaml. Note: the handlers:script must be a wsgi path to your flask app instantiation relative to where the process is started, not necessarily where app.yaml lives.

```yaml
runtime: python
runtime_config:
  python_version: 2
threadsafe: true
env: flex
handlers:
- script: flask.app
  secure: always
  url: /cron/.*
```

## Deploy

Deploy app and cron.yaml to Google Cloud

    $ gcloud app deploy
    $ gcloud app deploy cron.yaml

# Testing

    $ pytest -s tests.py
