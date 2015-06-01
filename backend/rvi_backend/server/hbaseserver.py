"""
Version: 0.1
HBase code for our RVI stuff put whatever notices, legal stuff, maintainer, etc...

"""

"""
Takes messages from Kafka message queue and inserts into HBase
For time being code is not modular... will update to create a table settings file
for future modurization.

HBase Sink which takes messages from Kafka message queue and inserts into HBase

NEW NOTE: WE WILL NOT BE DIRECTLY USING HBASE NOSQL... instead we will be using 
Apache Phoenix which is a SQL wrapper for HBASE.
"""

import os, threading, base64
from time import sleep
import Queue
from rvijsonrpc import RVIJSONRPCServer

import __init__
from __init__ import __RVI_LOGGER__ as logger

#import jaydebeapi, jpype
import json
from kafka import KafkaClient, SimpleConsumer
from starbase import Connection
import happybase

class HBaseServer(threading.Thread):
    """
    HBase thread that will continuously read from Kafka queue
    """

    def __init__(self, kafka_url, kafka_topic, hbase_url, hbase_rest_port):
        threading.Thread.__init__(self)
        self.kafka = KafkaClient(kafka_url)
        self.topic = kafka_topic
        self.hbase_connect = happybase.Connection(hbase_url)
        self.server_on_flag = True        
        self.cons = SimpleConsumer(self.kafka, None, self.topic)
        self.cons.seek(0,2)
        self.m = None
        self.car_table = self.hbase_connect.table('rvi')
        self.payload = None
        self.vin = None
        self.time = None
        self.data = None
        self.row_key = None
        self.count = 0
        self.sql_insert = None 

    def run(self):
        while self.server_on_flag:

            self.m = self.cons.get_message(block=False)
           
            if (self.m is not None):
                self.payload = json.loads(self.m.message.value)
                self.vin = str(self.payload['vin'])
                self.time = str(self.payload['timestamp'])
                self.data = str(self.payload['data'])
                
                self.row_key = self.vin+self.time
                try:
                    self.car_table.put(self.row_key,{'car:data':self.data})
                    self.count = self.count + 1
                    logger.info('HBase Server: key: %s, table: %s, car{data: %s}. Message number: %s', self.row_key, 'rvi', self.data, str(self.count))     
           
                except Exception as e:
                    logger.info('%s,Data Push into HBase unsuccessful...', e)

            else:
                sleep(1/5)

    def shutdown(self):
        self.server_on_flag = False
        logger.info('HBase Server shutting down...')




