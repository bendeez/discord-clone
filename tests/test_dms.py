import requests
from test_authentication import get_authorization_header

SERVER = "http://app:8000"


def test_get_dms():
    headers = get_authorization_header("Blaziken","1234")
    response = requests.get(f"{SERVER}/dms", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for d in data:
        dm_id = d["id"]
        response = requests.get(f"{SERVER}/dmmessages/{dm_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(data)
        assert isinstance(data,list)



