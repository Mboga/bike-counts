# bike-counts
Public dataset of brussels bike counts for the year 2019 - 2024
- This dataset is rich and can be used for time-series analysis in urban mobility

# tools
- polars
- docker
- postgresql database
- api requests
- matplotlib, seaborn


# development environment

we will do the development using docker-compose.

- Verify docker is running 

```
docker info
```

- Build and run the services

```
docker compose up --build
```
- Ensure port 5432 is free for postgres

```
sudo lsof -i :5432
```

- In case of running instance, note the PID and run:

```
sudo kill -9 PID
```

- Lauch the jupyter notebook for exploratory data analysis: 

```
http://127.0.0.1:8888/lab?token=2d31d5eacf2c4ef3f17fdc9b620a085d7270291b799462e0
```
# data
 The data is stored in /output/final_clean_data.csv

The data contains the following attributes:
```
id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP 
    device_name VARCHAR(255), 
    count BIGINT,            t
    average_speed DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    easting DOUBLE PRECISION,
    northing DOUBLE PRECISION
```
# contact

- for comments, contributions, reach out to nicholus.mboga@savanna-ai.be
- material created by Savanna AI (https://savanna-ai.be)

© 2025, Savanna-AI and Nicholus Mboga, nicholus.mboga@savanna-ai.be
All rights reserved: Software for Teaching purposes only. For any commercial use contact nicholus.mboga@savanna-ai.be

