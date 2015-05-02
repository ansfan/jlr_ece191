### Logical Steps
Definition: Client and Server; where client is our webapp and our server is our Apache datacenter.

1. Client asks server for data. Client will also tell server what is its return address, and type of data requested. You will fake the request with:
curl --data "source=http://127.0.0.1:8081/webhook/&car_name=ram" http://127.0.0.1:8080/webhook/

2. Server will store the client address, and prepare data for transport.
3. Each line of data will be packaged as a request, and sent to redis in a message queue with path /0/.
4. Celery will be reading on redis at path /0/ and detect each request and send the data. 