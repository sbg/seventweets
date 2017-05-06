from fabric.api import local, run, env, settings

env.user = 'root'
env.hosts = ['break.sedamcvrkuta.com:22202']

network_name = 'workshop'
image_tag = 'delicb/workshop'
db_container_name = 'workshop-postgres'
db_user = 'workshop'
db_name = 'seventweets'
db_port = 5432
db_image = 'postgres:9.6.2'
db_volume = 'workshop-postgres-data'

gunicorn_port = 8000
external_port = 80

service_container_name = 'seventweets'


def create_network():
    """
    Creates network for communication between different docker containers
    needed for seventweets to work. If network already exists, this command
    will not fail.
    """
    with settings(warn_only=True):
        run(f'docker network create {network_name}')


def create_volume():
    """
    Creates volume for data storage for postgres DB. If volume already exists
    it will be kept and command will not fail.
    """
    with settings(warn_only=True):
        run(f'docker volume create {db_volume}')


def start_db(db_pass):
    """
    Starts postgres database. If database is already running, it will 
    keep running.
    :param db_pass: Database password to use. 
    """
    with settings(warn_only=True):
        run(f'docker run -d --name {db_container_name} --net {network_name} '
            f'-v {db_volume}:/var/lib/postgresql/data '
            f'--restart unless-stopped -e POSTGRES_USER={db_user} '
            f'-e POSTGRES_PASSWORD={db_pass} '
            f'-e POSTGRES_DB={db_name} '
            f'-p 127.0.0.1:{db_port}:{db_port} {db_image}')


def pull_image(image=image_tag):
    """
    Pulls image with provided name and tag.
    :param image: Reference to image to pull. 
    """
    run(f'docker pull {image}')


def migrate(db_pass, image=image_tag):
    """
    Performs migrations on database.
    
    :param db_pass: Password for database. 
    :param image: Name of seventweets image.
    """
    run(f'docker run '
        f'--rm '
        f'--net {network_name} '
        f'-e ST_DB_USER={db_user} -e ST_DB_PASS={db_pass} '
        f'-e ST_DB_HOST={db_container_name} '
        f'-e ST_DB_NAME={db_name} '
        f'{image} '
        f'python3 -m seventweets migrate')


def start_service(db_pass, api_token, image=image_tag):
    """
    Starts seventweets service.
    
    :param db_pass: Password for database. 
    :param api_token: API token to use.
    :param image: Name of seventweets image.
    :return: 
    """
    run(f'docker run -d '
        f'--name {service_container_name} '
        f'--net {network_name} '
        f'-e ST_DB_USER={db_user} '
        f'-e ST_DB_PASS={db_pass} '
        f'-e ST_DB_HOST={db_container_name} '
        f'-e ST_DB_NAME={db_name} '
        f'-e ST_DB_PORT={db_port} '
        f'-e ST_API_TOKEN={api_token} '
        f'-p 0.0.0.0:{external_port}:{gunicorn_port} '
        f'{image}')


def check_db_connection(db_pass, image=image_tag):
    """
    Tries to connect to database for max 10 seconds.
    
    This is useful to check if communication between service and database
    is working and allows waiting for database to become responsive (relevant
    only for first deploy mostly).
    
    :param db_pass: Password for database. 
    :param image: Name of seventweets image.
    """
    run(f'docker run --rm '
        f'--net {network_name} '
        f'-e ST_DB_USER={db_user} '
        f'-e ST_DB_PASS={db_pass} '
        f'-e ST_DB_HOST={db_container_name} '
        f'-e ST_DB_NAME={db_name} '
        f'-e ST_DB_PORT={db_port} '
        f'{image} '
        f'python -m seventweets test_db -v -t 10')


def stop_service():
    """
    Stops seventweets service. If it is not running, command will not fail.
    """
    with settings(warn_only=True):
        run(f'docker stop {service_container_name}')
        run(f'docker rm {service_container_name}')


def build_image(image=image_tag):
    """
    Builds seventweets image locally.
    :param image: Name to give to image. 
    """
    local(f'docker build -t {image} . --build-arg PORT={gunicorn_port}')


def push_image(image=image_tag):
    """
    Pushes seventweets image to docker hub.
    :param image: Name of image to push. 
    """
    local(f'docker push {image}')


def app_logs():
    """
    Prints seventweets logs (stdout) from remote server.
    """
    run(f'docker logs {service_container_name}')


def deploy(db_pass, api_token, image=image_tag):
    """
    Builds and deploys application.
    
    This command will:
    - build seventweets image locally
    - push image to docker hub
    - create network on remote server
    - stop existing seventweets service on server
    - create volume on server
    - start database on server
    - pull new seventweets image on server
    - check if database connection is working
    - perform database migrations
    - start seventweets service
    
    :param db_pass: Password for database. 
    :param api_token: API token for protected API endpoints on seventweets.
    :param image: Name of image to use.
    """
    build_image(image)
    push_image(image)

    create_network()
    stop_service()
    create_volume()
    start_db(db_pass)
    pull_image(image)
    check_db_connection(db_pass)

    migrate(db_pass)
    start_service(db_pass, api_token, image)
