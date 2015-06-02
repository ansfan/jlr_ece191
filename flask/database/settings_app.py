# Flask
SECRET_KEY = 'secret!'

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# RVI
DATABASE_WEBHOOK_URL = 'http://52.25.32.18:8123/webhook/'
FLASK_WEBHOOK_URL = 'http://52.24.215.226/webhook/'
RVI_KAFKA_ENDPOINT = 'master:6667'

HBASE_IP = '172.31.17.174'
HBASE_TABLE = 'rvi'
