import pytest
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir), "tests/integration", "docker-compose.yml"
    )

def is_mongo_responsive(ip, port):
    client = MongoClient(
        "mongodb://root:example@{}:{}/".format(ip, port)
    )
    try:
        client.admin.command('ismaster')
        return True
    except ConnectionFailure:
        return False

@pytest.fixture(scope="session")
def mongo_service(docker_ip, docker_services):
    port = docker_services.port_for("mongodb", 27017)
    docker_services.wait_until_responsive(
        timeout=90.0, pause=0.1, check=lambda: is_mongo_responsive(docker_ip, port)
    )
    return (docker_ip, port)