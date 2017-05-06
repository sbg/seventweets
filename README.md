# Seven Tweets project

The idea of this project is to build a network of mini services that are similar to Twitter. In this network, node is
a separate service with it's own storage (database) and username which serves as a unique identifier.

Every node in the network knows address of other nodes in order to communicate with them. All of the nodes have
same API, but implementation might differ. 

Nodes can run on its own, without joining network. To join network, request to `/join_network` is issued with address
of at least one other node. This initiates protocol for joining. New node sends request with its own name and address
to existing node and receives list of other nodes in network as result. Existing node adds him to his own list and
new node registers itself to all other nodes by sending its info to `/register`. When node is being shut down, it sends
`/unregister` request to all other nodes.

If node is killed violently before it has a chance to unregister itself from network, other nodes will remove it from
list upon unsuccessful contact with it.

Basic node functionality is to:
- create tweets
- create retweets (references to other nodes by name, not address, since we allow address to change)
- list tweets
- delete tweets
- local search (only one node)
- distributed search (search on all nodes in network and return aggregated results)

SevenTweets is written in `Python 3` with `Flask` framework and `PostgreSQL` database.

Build packages source into Docker image and automated deploy is implemented using `fabric3`.


## Getting Started

### Prerequisites 
In order to run and develop SevenTweets, [Python 3.6+](https://www.python.org/downloads/) is required.

It is suggested to run local database in Docker container as per instructions provided on 
[official PostgreSQL docker image](https://hub.docker.com/_/postgres/). Example of running it can be found in
`fabfile.py` which is included in source code.


## Running the tests

For writing tests and executing them, SevenTweets uses [pytest](https://docs.pytest.org/en/latest/). It needs to
be installed together with all other dependencies listed in `requirements-dev.txt` file.

To run tests, simply activate virtual environment (if you are using one, and you should) and execute command `pytest`
inside of root directory of the source.

You can run tests through the Python interpreter from the command line:


## Deployment

In order to deploy SevenTweets provided `fabfile.py` can be used.

Specific steps can be invoked, but in order to execute all steps, fabric deploy action can be used. There are some
default values (like host name and user to be used) that can be overriden by providing fabric environment variables.
`fabfile.py` also contains default names of Docker image and container that you might want to change.

Two required parameters are database password and API token. For example, to deploy SevenTweets, following command
can be used:
```
fab deploy:db_pass=SomeSecureDatabasePassword,api_token=RandomlyGeneratedToken -I -H "myserver.example.com"
```

## Authors

* Marija Ševković <marija.sevkovic@sevenbridges.com>
* Bojan Delic <bojan.delic@sevenbridges.com>
* Toni Ruza <toni.ruza@sevenbridges.com>
* Jovan Cejovic <jovan.cejovic@sevenbridges.com>


## License

This project is licensed under the Apache 2 License - see the LICENSE.txt for details
