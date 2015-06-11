### Logical Steps
Definition: Database and Web; where database is our web framework which connects to our Hadoop setup, and web is our webapp that manages user sessions. Database web framework is called app.py, and user web framework is called client.py.

1. Client.py asks app.py for data. Client.py will also tell server what is its return address, and type of data requested.
2. app.py will store the client address, and request Apache Kafka or HBase, depending on requested data.
3. app.py will prepare data for transport, using the return address specified.
3. client.py will listen on /webhook/ if its a real-time data packet. if pulling historical data, packet will go through normal HTTP POST response.

### To Deploy
# Deploying app.py
1. pip install -r requirements.txt
2. Configure database/settings_app.py
3. python database/app.py
4. point to localhost:5000

# Deploying client.py
1. pip install -r requirements.txt
2. sudo apt-get install nginx
3. copy in this code as rvi.conf into /etc/nginx/sites-available/rvi.conf:

server {
    listen 80;
    server_name localhost;
    access_log /var/log/nginx/example.log;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_redirect off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_redirect off;
        proxy_buffering off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}

4. sudo service nginx restart
5. Configure web/settings_client.py
6. python web/client.py
7. point to localhost:5000