import re
import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.utils.response_formatter import pack_response


def test_pack_response_includes_keys():
    data = [{'id': 1}, {'id': 2}]
    result = pack_response('data', data, count_key='count')
    assert result['rsp_code'] == '00000'
    assert result['rsp_msg'] == '정상처리'
    assert result['data'] == data
    assert result['count'] == len(data)
    # search_timestamp is included and is numeric string
    assert re.match(r"^\d{14}$", result['search_timestamp'])


try:
    from fastapi.testclient import TestClient
    from app.main import app
except Exception:  # httpx may not be installed
    TestClient = None
    app = None


@pytest.mark.skipif(TestClient is None, reason="TestClient unavailable")
def test_root_endpoint():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Custom MyData API"}
