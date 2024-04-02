import requests

SERVER = "http://app:8000"

def get_authorization_header(username,password):
    payload = {"username":username,"password":password}
    response = requests.post(f"{SERVER}/login",json=payload)
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]
    headers = {"Authorization":f"Bearer {token}"}
    return headers

def test_authentication():
    payload = {"username": "Blaziken", "password": "1234"}
    response = requests.post(f"{SERVER}/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data