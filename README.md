# Seven Tweets project

The idea of this project is to build a network of mini services that are similar to Twitter. In this network, node is
a separate service with it's own storage(database) and username which serves as a unique identifier.

Every node in the network knows addresses of other nodes in the same network. All of them have the identical implementation 
and the only difference is in the starting arguments. Each service receives one address at start-up and gets other addresses 
from reference node (exception is the first node in the network). Then he sends register requests to others, so they can 
add him to the nodes list. Also, before shutdown, node sends unregister request to all nodes in the network and they 
remove him from their list.

Every post is saved locally in the database but it's content is available to all others in the network. Users can post 
tweets, re-tweets, modify and delete them or list all posts(tweets and re-tweets) from one node. They can also search 
posts in the network by specific query arguments. In this case every node receives request with query arguments, 
finds matching 
tweets and re-tweets in the local database and sends the results back. Final results are 
assembled and displayed by node which requested search. When posting re-tweet only reference to original tweet is 
preserved in the local database. Re-tweet content is dynamically obtained per request. 

Seven Tweets app is written in Python3 and Flask framework. Because Flask’s built-in server is not suitable for 
production the app has production mode which runs with Gunicorn server.

## Getting Started

### Prerequisites 

You need to install [Python](https://www.python.org/downloads/) 3.4.3 or higher and 
[Postgresql](https://www.postgresql.org/download/) database on your machine. 

Next, you have to create users and their databases either manually or by supplying desired username and database name to
`create_db.sh` script in the bin directory of the project (script is written for Linux and assumes existence of postgres user).

```
# give execution right to script
$ chmod +x create_db.sh
# create user and db in postgres
$ ./create_db.sh username db_name
```

### Installing


Other software that needs to be installed is listed in requirements-dev.txt. If you do not want to start tests you can 
install just requirements.txt.

It's recommended to create [virtual environment](https://docs.python.org/3/library/venv.html) 
and then install necessary software in that environment like this:

```
$ source path-to-env/bin/activate
$ pip install -r requirements-dev.txt
```

For initiating database and running the service we will use `start.py` script in seventweets directory.

You can initiate database with :
```
$ python start.py --dbname=yourdatabase --sname=username init_db 
```
This will create table tweets and insert some default data you can change.

Run the first service with:
```
$ python start.py --dbname=yourdatabase --sname=username run_server --port=num-of-port
```
and all next services with:
```
$ python start.py --dbname=yourdatabase --sname=username run_server --port=num-of-port --con=ip:port
```
where `--con` parameter is the address of one node already in the network.

Note that you need to have your Postgresql server running during this.

### Endpoints list

*/path, request method {json body parameters}*

* /register , method=POST {port, name} 
    * Handles register request and adds node to the list of nodes
    * port - port on where service sending request is listening 
    * name - service username 
* /unregister/*string:name* , method=DELETE 
    * Handles unregister request and removes node from the list
    * name - username to delete from the list of nodes
* /retweet , method=POST {name , id} 
    * Handles request for creation of re-tweet 
    * name - username of the node which contains referenced tweet 
    * id - id of the referenced tweet
* /tweets , method=POST {tweet} 
    * Handles request for creation of tweet
    * tweet - tweet message
* /tweets/*int:id* , method=DELETE 
    * Handles request for deleting tweet
    * id - tweet id
* /tweets/*int:id* , method=PUT {tweet} 
    * Handles request for update of tweet content 
    * tweet - new tweet message
* /tweets/*int:id* , method=GET 
    * Handles get request for specific tweet
    * id - tweet id
* /tweets , method=GET 
    * Handles get request for all tweets on that node
* /search , method=GET 
    * Handles search request. Search is spread through network. 
    * Available search parameters: 
        * content - search tweets by content
        * name - search only on specific node
        * from_time - search tweets created after date yyyy-mm-dd hh:mm:ss
        * to_time - search tweets to this date yyyy-mm-dd hh:mm:ss
        * per_page - number of results per page
        * last_creation_time - creation time of the last tweet in the page
* /search_me, method=GET 
    * Search is done only on that node. Search parameters are the same as above.

At the moment application doesn't have UI and requests can be sent via HTTP clients (e.g. curl or [Postman](https://www.getpostman.com/)).

Note that implementation requires proper `Content-Type` header to be set to `application/json` when submitting data. 
Response code 400 will be returned if this is not the case.

## Running the tests

You can run tests through the Python interpreter from the command line:

```
$ python -m pytest path-to-tests-dir
```
This is almost equivalent to invoking the command line script pytest path-to-tests-dir directly, 
except that python will also add the current directory to sys.path .

Tests directory contains example api and unit tests for Seven Tweets.

## Production mode

Seven Tweets app also have support for Gunicorn server and remote database.

Configuration for database can be set in `config/db_conf.yaml` file. If that file doesn't exists service
will try to connect to local database.

In the config directory there are 2 example configs for gunicorn server, 2 example for nodes config and 1 db_conf example.

You can install Gunicorn with:
```
$ pip install gunicorn
```

and run node with gunicorn:
```
$ gunicorn --config=config/gunicorn.py wsgi
```
This runs the Gunicorn server with `wsgi.py` file in the root directory which supplies callable app.
Note that for the next service you must run Gunicorn with different config file and different 
node config. Change wsgi.py to read new node config file or create another wsgi.

Note that there are some known issue with using gunicorn on some versions of Windows. 
It has been tested on Linux and OSX. In case windows is required, using [Docker](https://www.docker.com/) can be easy solution.

## Authors

* Marija Ševković <marija.sevkovic@sbgenomics.com> - *Seven Bridges Genomics Inc.* 

## License

This project is licensed under the Apache 2 License - see the LICENSE.txt for details
