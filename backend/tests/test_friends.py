from app.models.friends import Friends
from app.models.friend_requests import FriendRequests
from app.models.user import Users
from utils import RequestMethod


async def test_create_friend(http_request,usernames,tokens,clean_up_data,undelete_data):
    """
        user with username of usernames[0] sent a friend request to use with username
        usernames[3]
    """
    json = {"username":usernames[0]}
    response = await http_request(path="/friend",method=RequestMethod.POST,json=json,token=tokens[usernames[3]])
    data = await response.json()
    assert response.status == 201
    assert data == {"id":data["id"],"sender":usernames[0],"receiver":usernames[3]}
    await clean_up_data(Friends,id=data["id"])
    await undelete_data(FriendRequests,sender=usernames[0],receiver=usernames[3])

async def test_invalid_create_friend_by_being_sender(http_request,usernames,tokens):
    """
        usernames[0] who sent the friend request cannot accept the friend request which creates a friend
        relationship
    """
    json = {"username":usernames[3]}
    response = await http_request(path="/friend",method=RequestMethod.POST,json=json,token=tokens[usernames[0]])
    assert response.status == 403

async def test_invalid_create_friend_by_already_friends(http_request,usernames,tokens):
    """
        users with usernames of usernames[0] and usernames[1] are already friends
    """
    json = {"username":usernames[1]}
    response = await http_request(path="/friend",method=RequestMethod.POST,json=json,token=tokens[usernames[0]])
    assert response.status == 409

async def test_invalid_create_friend_by_no_friend_request(http_request,usernames,tokens):
    """
        users with usernames of usernames[0] and usernames[2] have no friend request
    """
    json = {"username":usernames[2]}
    response = await http_request(path="/friend",method=RequestMethod.POST,json=json,token=tokens[usernames[0]])
    assert response.status == 409

async def test_get_friends(http_request,usernames,get_user_by_username_index,tokens):
    """
        users with usernames of usernames[0] and usernames[1] are friends
        they also have a dm
    """
    remote_user = await get_user_by_username_index(1,load_attributes=[(Users.received_dms,)]) # remote user has only one received dm
    response = await http_request(path="/friends", method=RequestMethod.GET, token=tokens[usernames[0]])
    data = await response.json()
    assert response.status == 200
    assert data == [{"status":remote_user.status,"username":remote_user.username,"profile":remote_user.profile,
                       "dmid":remote_user.received_dms[0].id}]

async def test_delete_friend(http_request,usernames,tokens,undelete_data):
    """
         users with usernames of usernames[0] and usernames[1] are friends
    """
    json = {"username": usernames[1]}
    response = await http_request(path="/friend", method=RequestMethod.DELETE, json=json,
                                  token=tokens[usernames[0]])
    assert response.status == 204
    await undelete_data(Friends,sender=usernames[0],receiver=usernames[1])

async def test_invalid_delete_friend(http_request,usernames,tokens,undelete_data):
    """
         users with usernames of usernames[0] and usernames[2] are not friends
    """
    json = {"username": usernames[2]}
    response = await http_request(path="/friend", method=RequestMethod.DELETE, json=json,
                                  token=tokens[usernames[0]])
    assert response.status == 403
