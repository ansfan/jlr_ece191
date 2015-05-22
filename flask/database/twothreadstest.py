
from rviwebconsumer import RVIConsumer

vin1 = RVIConsumer('172.31.42.145:6667', 'rvi', 'new_abniar', 'http://52.24.215.226/webhook/')
vin1.start()

vin2 = RVIConsumer('172.31.42.145:6667', 'rvi', 'new_abnovkak', 'http://52.24.215.226/webhook/')
vin2.start()



