# Spiders
Flask app to records data about your tarantulas. You are able to record data as feeding schedule, molts and you can add images of your tarantula with notes. All of that can be also modified in the case of entering mistaken data. Web app also enables you to add your specific species of tarantulas (species are not hard coded and you are supposedto add them yourself).


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
## Examples of web app
### Main page
#### Main page is an index of your tarantulas
*To access specific data of a tarantulas or any spider click on its name.*
![main page](https://github.com/ar3s-xss/Spiders/blob/main/images/main_page.png)
### Species
#### Species allows you to add, modify or delete species
![species](https://github.com/ar3s-xss/Spiders/blob/main/images/species.png)
### Add spiders
#### Add spiders allow you to add your tarantula/s
![add spider](https://github.com/ar3s-xss/Spiders/blob/main/images/add_spider.png)
### Details of spider
As mentioned above to access specific tarantulas details click on the **name** of desired tarantula.
This page allows you to add, modify or delete feeding history, molts and images.
![spider details](https://github.com/ar3s-xss/Spiders/blob/main/images/details_of_spider.png)
