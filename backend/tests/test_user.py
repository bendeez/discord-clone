from utils import RequestMethod
from app.core.oauth import get_current_user


async def test_login(http_request,current_user):
    response = await http_request(path="/login",
                                  method=RequestMethod.POST,
                                  json={"username":current_user.username,"password":current_user.password})
    assert response.status_code == 200
    data = response.json()
    user = await get_current_user(data["access_token"])
    assert user == current_user

async def test_invalid_login(http_request,current_user):
    response = await http_request(path="/login",
                                  method=RequestMethod.POST,
                                  json={"username": current_user.username, "password": "wrong password"})
    assert response.status_code == 401

async def test_create_user(http_request):
    username = "test"
    json = {"email":f"{username}@gmail.com","username": username, "password": "1234"}
    response = await http_request(path="/user",
                                  method=RequestMethod.POST,
                                  json=json)
    assert response.status_code == 201
    data = response.json()
    assert data == {"email":json["email"],"username":json["username"]}

async def test_invalid_create_user(http_request,current_user):
    """
        the username already exists
    """
    response = await http_request(path="/user",
                                  method=RequestMethod.POST,
                                  json={"email": f"{current_user.username}@gmail.com",
                                        "username": current_user.username, "password": "1234"})
    assert response.status_code == 409

async def test_update_user_profile(http_request,current_user_token):
    response = await http_request(path="/profilepicture",
                                  method=RequestMethod.PUT,
                                  files={"file":open("./tests/programming.jfif","rb")},
                                  token=current_user_token)
    assert response.status_code == 200
    data = response.json()
    assert data["profile"].startswith("https://firebasestorage.googleapis.com")

async def test_get_user_credentials(http_request,current_user,current_user_token):
    response = await http_request(path="/usercredentials", method=RequestMethod.GET,token=current_user_token)
    assert response.status_code == 200
    data = response.json()
    assert data == {"username":current_user.username,"profile":current_user.profile}

async def test_unauthorized(http_request):
    response = await http_request(path="/usercredentials", method=RequestMethod.GET)
    assert response.status_code == 401