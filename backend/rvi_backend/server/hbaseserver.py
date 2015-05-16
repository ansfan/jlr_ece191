"""
Version: 0.1
HBase code for our RVI stuff put whatever notices, legal stuff, maintainer, etc...

"""

"""
Takes messages from Kafka message queue and inserts into HBase
For time being code is not modular... will update to create a table settings file
for future modurization.

HBase Sink which takes messages from Kafka message queue and inserts into HBase
"""

import os, threading, base64
from time import sleep
import Queue
from rvijsonrpc import RVIJSONRPCServer

import __init__
from __init__ import __RVI_LOGGER__ as logger

import json
from kafka import KafkaClient, SimpleConsumer
from starbase import Connection

class HBaseServer(threading.Thread):
    """
    HBase thread that will continuously read from Kafka queue
    """

    def __init__(self, kafka_url, kafka_topic, hbase_url, hbase_rest_port):
        threading.Thread.__init__(self)
        self.kafka = KafkaClient(kafka_url)
        self.topic = kafka_topic
        self.hbase_connect = Connection(host=hbase_url, port=hbase_rest_port)
        self.server_on_flag = True        
        self.cons = SimpleConsumer(self.kafka, None, self.topic)
        self.cons.seek(0,2)
        self.m = None
        self.car_table = None
        self.payload = None
        self.vin = None
        self.time = None
        self.data = None

    def run(self):
        
        while self.server_on_flag:

            self.m = self.cons.get_message(block=False)
           
            if (self.m is not None):
                self.payload = json.loads(self.m.message.value)
                self.vin = self.payload['vin']
                self.time = self.payload['timestamp']
                self.data = self.payload['data']

                self.car_table = self.hbase_connect.table(self.vin)
                
                if self.car_table.exists() is not True:
                    self.car_table.create('geo','car')
                
                if self.car_table.insert(self.time,{'geo':{'data':self.data}}) == 200:
                    logger.info('HBase Server: key: %s, table: %s, Geo{data: %s}.', self.time, self.vin, self.data)

                else:
                    logger.info('Data Push into HBase unsuccessful...')


            else:
                sleep(1/5)

    def shutdown(self):
        self.server_on_flag = False
        logger.info('HBase Server shutting down...')




