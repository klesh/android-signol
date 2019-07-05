import pytest
from os import path, environ

TESTS_PATH = path.dirname(path.realpath(__file__))
ROOT_PATH = path.dirname(TESTS_PATH)
ARTIFACTS_PATH = path.join(TESTS_PATH, 'artifacts')

@pytest.fixture
def app_debug_apk_path():
    return path.join(ARTIFACTS_PATH, 'app-debug.apk')

@pytest.fixture
def app_release_apk_path():
    return path.join(ARTIFACTS_PATH, 'app-release.apk')

@pytest.fixture
def app_release_signed_apk_path():
    return path.join(ARTIFACTS_PATH, 'app-release-signed.apk')

@pytest.fixture
def ks_path():
    return path.join(ARTIFACTS_PATH, 'testkey.jks')

@pytest.fixture
def ks_pass():
    return 'helloworld'

@pytest.fixture
def key_alias():
    return 'hello'

@pytest.fixture
def key_pass():
    pass

@pytest.fixture
def server_host():
    return 'localhost'

@pytest.fixture
def server_port():
    return 19283

@pytest.fixture
def sign_key():
    return 'pseudorandom key'

@pytest.fixture
def app_path():
    return path.join(ROOT_PATH, 'src', 'app.py')
