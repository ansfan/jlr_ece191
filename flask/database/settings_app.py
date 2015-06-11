# Flask
SECRET_KEY = 'secret!'

# RVI
# The public IP of where this database web server is deployed
FLASK_WEBHOOK_URL = 'http://52.24.215.226/webhook/'
# Endpoint to access Apache Kafka
RVI_KAFKA_ENDPOINT = 'master:6667'
# Kafka Topic
RVI_KAFKA_TOPIC = 'rvi'

# HBase
# IP which hosts the HBase
HBASE_IP = 'master'
# Name of table to be accessed
HBASE_TABLE = 'rvi'
