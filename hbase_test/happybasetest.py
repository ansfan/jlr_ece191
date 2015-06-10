import happybase
from kafka import KafkaClient, SimpleConsumer

#kafka_consumer = SimpleConsumer(KafkaClient('172.31.17.174:6667'), None, 'rvi')
#kafka_consumer.seek(0,2)
hb_conn = happybase.Connection('172.31.17.174')
table = hb_conn.table('rvi')
"""
for key, data in table.scan(row_prefix="3"):
    print key, data
"""

vin ='rsixtbmw'

row = table.row('rjsram')
print row
"""
if len(row)==0:
	print "nothing!"
else:
	print row['user:mostrecent']
"""
#vin = '3'
#start_date = '10000000'
#end_date = '20000000'

#start_key = vin+start_date
#end_key = vin+end_date
count = 0
for key, data in table.scan(row_prefix=vin):
    count = count + 1
    print key,data, count
"""
max_time = 0

#for key, data in table.scan(row_start=start_key, row_stop=end_key):
for key, data in table.scan(row_prefix=vin):
    
    timestamp = int(key[len(vin):])
    
    if timestamp > max_time:
        max_time = timestamp
    else:
        pass


    #data['data'] = data.pop('car:data')
    #data['vin'] = vin
    #data['timestamp'] = timestamp
    #payload.append(data)
    

print max_time
#print len(payload)
"""
