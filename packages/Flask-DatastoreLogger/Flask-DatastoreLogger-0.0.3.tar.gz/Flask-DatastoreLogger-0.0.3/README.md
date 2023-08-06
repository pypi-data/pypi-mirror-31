# Flask-DatastoreLogger

A logging interface for Google Cloud Datastore

## Installation

Add this line to your application's requirements.txt

```python
Flask-DatastoreLogger
```

And then execute:

    $ pip install -r requirements.txt

Or install it yourself as:

    $ pip install Flask-DatastoreLogger

## Usage

Using DatastoreLogger is dead simple. First set your GOOGLE_APPLICATION_CREDENTIALS environment variable to point at a valid JSON creds file.

    $ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json

The following snippet should get you coding
```python
import logging
from flask import Flask
from DatastoreLogger import DatastoreLog, DatastoreLogHandler
from PubSubDecorator import PubSubDecorator


app = Flask(__name__)
app.pubsub = PubSubDecorator(app)

@app.pubsub.subscribe(
    subscription='run_task'
    topic='task_queue',
    route='/run_task',
    methods=['POST']
)
def run_task(message, *args, **kwargs):
    task_id = message.get('task_id')

    task_logger = logging.getLogger('task_log_{0}'.format(task_id))
    handler = DatastoreLogHandler('task_log', task_id)

    task_logger.addHandler(handler)
    task_logger.setLevel(logging.DEBUG)

    task_logger.info('Starting Task #{0}'.format(task_id))

    # process task actions logging messages with task_logger

    return '', 200


@app.route('/task_log/<int:task_id>', methods=['GET'])
def task_log(task_id):
    log = DatastoreLog('task_log', task_id)
    return log.stream_response()
```

# Testing

    $ pytest -s --show-capture=no tests.py
