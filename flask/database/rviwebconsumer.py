import json, time, threading
from kafka import KafkaClient, SimpleConsumer
from kafka.partitioner.base import  Partitioner
import requests

class RVIConsumer(threading.Thread):

    def __init__(self, kafka_addr, topic, vin, web_url):
        threading.Thread.__init__(self)

        self.kafka = KafkaClient(kafka_addr) #kafka_addr
        self.cons = SimpleConsumer(self.kafka, None, topic)
        self.cons.seek(0,2)

        self.vin = vin
        self.web_url = web_url 
        self.flag = True
        self.count = 0
        self.sleep_count = 0
        self.headers = {'Content-Type' : 'application/json'}

    def is_running(self):
        return self.flag
        
    def run(self):
        while self.flag:
            
            #cons = SimpleConsumer(kafka, None, 'rvi')
            m = self.cons.get_message(block=False)
            if (m is not None):
                payload = json.loads(m.message.value)

                if(payload['vin'] == self.vin):
                    self.sleep_count = 0 
                    payloadtoweb = json.dumps(m.message.value)
                    r = requests.post(self.web_url, data=payloadtoweb, headers=self.headers) 
                    if (r.status_code is 200):
                        print m.message.value + " sent successfully\n"        
                    else: 
                        print "%s is not available, status code:%d...shutting down now..."%(self.web_url,r.status_code)
                        self.shutdown()       

            else:
                if (self.sleep_count > 100000):
                    print "No new data for %s... Timing out" % self.vin
                    self.shutdown()

                time.sleep(1/5)
                self.sleep_count = self.sleep_count + 1

    def shutdown(self):
        self.flag = False    
        requests.post(self.web_url, data=json.dumps({'vin':self.vin, 'data':'EOM'}), headers=self.headers) 
        print "%s consumer thread shutting down" % self.vin 
 
