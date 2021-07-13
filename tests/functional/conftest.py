import uuid

import pytest


APP_URL = 'http://localhost:8080'


@pytest.fixture
def operation_id():
    return str(uuid.uuid4())
