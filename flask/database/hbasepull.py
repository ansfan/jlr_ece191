import json, time, happybase
import settings_app as settings
class RVIHBaseTable:
    
    def __init__(self):
        try:
            self.hb_connection = happybase.Connection(settings.HBASE_IP)
            self.hb_table = self.hb_connection.table(settings.HBASE_TABLE)
        except Exception as e:
            print 'Could not connect to hbase with error ', e

    def query_by_date(self, vin, start_time, end_time):
        start_key = vin+start_time
        end_key = vin+end_time
        
        payload = []
        for key, data in self.hb_table.scan(row_start = start_key, row_stop = end_key):
            timestamp = key[len(vin):]
            data['data'] = data.pop('car:data').encode('ascii')
            data['vin'] = vin
            data['timestamp'] = timestamp
            payload.append(data)

        payloadtoweb = {}
        payloadtoweb['payload'] = payload
        payloadtoweb = json.dumps(payloadtoweb)        

        return payloadtoweb

    def max_date(self, vin):
        
        try: 
            #use vin as key for car data
            row = self.hb_table.row(vin)
            max_date = row['user:mostrecent']
            return str(max_date)
        except Exception as e:
            print 'Could not get car info with error ', e
            max_date = 0
            return str(max_date)
