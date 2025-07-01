# bike-counts
Public dataset of brussels bike counts 


# create environment

```
python3 -m venv bike_counts
source bike_count/bin/activate
pip install -r requirements.txt

```
 - install vscode container tools
 # development

 we will do the development using docker-compose.

Verify docker is running 

```
docker info
```

1. Build and run the services

```
docker compose up --build
```

sudo lsof -i :5432

postgres 305 postgres    7u  IPv6 0x15d2dbad2868639e      0t0  TCP *:postgresql (LISTEN)
postgres 305 postgres    8u  IPv4 0x850e08bc398d8590      0t0  TCP *:postgresql (LISTEN)
postgres


sudo kill -9 305

brew services start postgresql
brew services stop postgresql
brew services restart postgresql


paste the url in a browser file:///home/jovyan/.local/share/jupyter/runtime/jpserver-7-open.html
http://127.0.0.1:8888

http://9d5bb4682fc1:8888/lab?token=2d31d5eacf2c4ef3f17fdc9b620a085d7270291b799462e0

Then access your jupyter notebook