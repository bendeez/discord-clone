from utils import RequestMethod
from uuid import uuid4
from app.models.user import Users


async def test_login(http_request,usernames):
    json = {"username":usernames[0],"password":"1234"}
    response = await http_request(path="/login",method=RequestMethod.POST,json=json)
    data = await response.json()
    assert response.status == 200
    assert data["access_token"] is not None

async def test_invalid_login(http_request,usernames):
    json = {"username": usernames[0], "password": "wrong password"}
    response = await http_request(path="/login",method=RequestMethod.POST,json=json)
    assert response.status == 401

async def test_create_user(http_request,clean_up_data):
    username = str(uuid4())
    json = {"email":f"{username}@gmail.com","username": username, "password": "1234"}
    response = await http_request(path="/user", method=RequestMethod.POST, json=json)
    data = await response.json()
    assert response.status == 201
    assert data == {"email":json["email"],"username":json["username"]}
    await clean_up_data(Users,username=username)

async def test_invalid_create_user(http_request,usernames):
    """
        the username already exists
    """
    json = {"email": f"{usernames[0]}@gmail.com", "username": usernames[0], "password": "1234"}
    response = await http_request(path="/user", method=RequestMethod.POST, json=json)
    assert response.status == 409

async def test_update_user_profile(http_request,tokens,usernames,get_user_by_username_index):
    files = {"file":open("./tests/programming.jfif","rb")}
    response = await http_request(path="/profilepicture", method=RequestMethod.PUT, files=files,token=tokens[usernames[0]])
    data = await response.json()
    assert response.status == 200
    assert data["profile"].startswith("https://firebasestorage.googleapis.com")

async def test_get_user_credentials(http_request,tokens,get_user_by_username_index):
    current_user = await get_user_by_username_index(0)
    response = await http_request(path="/usercredentials", method=RequestMethod.GET,token=tokens[current_user.username])
    data = await response.json()
    assert response.status == 200
    assert data == {"username":current_user.username,"profile":current_user.profile}

async def test_unauthorized(http_request):
    response = await http_request(path="/usercredentials", method=RequestMethod.GET)
    assert response.status == 401