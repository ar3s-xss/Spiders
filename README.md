# Spiders
Flask app to records data about yours tarantulas


## Setup
First install all python libraries
```
pip install -r requirements.txt
```

### Run in docker
1.  cd into projects directory.
2.  Run docker compose do build it first & run.
    ```
    docker compose up --build -d
    ```
    After building the project just use 
    ```
    docker compose up -d
    ```

3.  To access web app type in browser **localhost:5000** when ran locally or **0[.]0[.]0[.]0:5000** if ran on server.
4. Stop web app
    ```
    docker compose down
    ```
