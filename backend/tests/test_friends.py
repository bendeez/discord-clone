from app.crud.friend_requests import create_friend_request
from app.crud.friends import create_friend, get_friend
from utils import RequestMethod


async def test_create_friend(http_request,current_user_token,current_user,remote_user,db):
    remote_user,_ = await remote_user()
    await create_friend_request(db=db,current_user=remote_user,remote_user_username=current_user.username)
    response = await http_request(path="/friend",method=RequestMethod.POST,
                                  json={"username":remote_user.username},
                                  token=current_user_token)
    assert response.status_code == 201
    data = response.json()
    assert data == {"id":data["id"],"sender":remote_user.username,"receiver":current_user.username}

async def test_invalid_create_friend_by_being_sender(http_request,current_user,remote_user,db):
    remote_user, remote_token = await remote_user()
    await create_friend_request(db=db,current_user=remote_user,remote_user_username=current_user.username)
    response = await http_request(path="/friend",method=RequestMethod.POST,
                                  json={"username":current_user.username},
                                  token=remote_token)
    assert response.status_code == 403

async def test_invalid_create_friend_by_already_friends(http_request,current_user,current_user_token,remote_user,db):
    remote_user,_ = await remote_user()
    friend_request = await create_friend_request(db=db, current_user=remote_user, remote_user_username=current_user.username)
    await create_friend(db=db,current_user=current_user,remote_user_username=remote_user.username,
                        current_friend_request=friend_request)
    response = await http_request(path="/friend",method=RequestMethod.POST,
                                  json={"username":remote_user.username},
                                  token=current_user_token)
    assert response.status_code == 409

async def test_invalid_create_friend_by_no_friend_request(http_request,current_user_token,remote_user):
    remote_user, _ = await remote_user()
    response = await http_request(path="/friend",method=RequestMethod.POST,
                                  json={"username":remote_user.username},
                                  token=current_user_token)
    assert response.status_code == 409

async def test_get_friends(http_request,current_user,current_user_token,remote_user,db):
    remote_user, _ = await remote_user()
    friend_request = await create_friend_request(db=db, current_user=remote_user,
                                                 remote_user_username=current_user.username)
    await create_friend(db=db, current_user=current_user, remote_user_username=remote_user.username,
                        current_friend_request=friend_request)
    response = await http_request(path="/friends", method=RequestMethod.GET, token=current_user_token)
    assert response.status_code == 200
    data = response.json()
    assert data == [{"status":remote_user.status,"username":remote_user.username,"profile":remote_user.profile,
                       "dmid":None}]

async def test_delete_friend(http_request,current_user,current_user_token,remote_user,db):
    remote_user, _ = await remote_user()
    friend_request = await create_friend_request(db=db, current_user=remote_user,
                                                 remote_user_username=current_user.username)
    await create_friend(db=db, current_user=current_user, remote_user_username=remote_user.username,
                        current_friend_request=friend_request)
    response = await http_request(path="/friend", method=RequestMethod.DELETE,
                                  json={"username":remote_user.username},
                                  token=current_user_token)
    assert response.status_code == 204
    friend = await get_friend(db=db,current_user=current_user,remote_user_username=remote_user.username)
    assert friend is None

async def test_invalid_delete_friend(http_request,current_user_token,remote_user):
    remote_user, _ = await remote_user()
    response = await http_request(path="/friend", method=RequestMethod.DELETE,
                                  json={"username": remote_user.username},
                                  token=current_user_token)
    assert response.status_code == 403
