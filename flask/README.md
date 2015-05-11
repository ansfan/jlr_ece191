### Logical Steps
Definition: Client and Server; where client is our webapp and our server is our Apache datacenter.

1. Client asks server for data. Client will also tell server what is its return address, and type of data requested.
2. Server will store the client address, and prepare data for transport.
3. Each line of data will be packaged as a request, and sent to redis in a message queue with path /0/.
4. Celery will be reading on redis at path /0/ and detect each request and send the data. 

### To Run
1. pip install flask && pip install requests && pip install celery && pip install kafka-python
2. python app.py
3. redis-server
4. celery worker -A app.celery --loglevel=debug
5. python client.py
6. point browser to 127.0.0.1:5000
