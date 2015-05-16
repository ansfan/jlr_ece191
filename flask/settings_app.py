# Flask
SECRET_KEY = 'secret!'

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# RVI
DATABASE_WEBHOOK_URL = 'http://127.0.0.1:8080/webhook/'
FLASK_WEBHOOK_URL = 'http://127.0.0.1:5000/webhook/'
RVI_KAFKA_ENDPOINT = '172.31.42.145:6667'