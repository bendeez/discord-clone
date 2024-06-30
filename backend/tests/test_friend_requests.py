from app.models.friend_requests import FriendRequests
from utils import RequestMethod

async def test_create_friend_request(http_request,usernames,tokens,clean_up_data):
    json = {"username":usernames[2]}
    response = await http_request(path="/friendrequest",method=RequestMethod.POST,json=json,token=tokens[usernames[0]])
    data = await response.json()
    assert response.status == 201
    assert data == {"id":data["id"],"sender":usernames[0],"receiver":usernames[2]}
    await clean_up_data(FriendRequests,id=data["id"])

async def test_invalid_create_friend_request(http_request,usernames,tokens):
    """
        users with usernames of usernames[0] and usernames[1] are already friends
    """
    json = {"username": usernames[1]}
    response = await http_request(path="/friendrequest", method=RequestMethod.POST, json=json,
                                  token=tokens[usernames[0]])
    assert response.status == 409

async def test_get_friend_requests(http_request,get_user_by_username_index,tokens):
    """
         user with username of usernames[0] sent a friend request to
         user with username of usernames[3]
    """
    current_user = await get_user_by_username_index(0)
    remote_user = await get_user_by_username_index(3)
    response = await http_request(path="/friendrequests", method=RequestMethod.GET,
                                  token=tokens[current_user.username])
    data = await response.json()
    assert data == [{"sender":current_user.username,"senderprofile":current_user.profile,
                       "receiver":remote_user.username,"receiverprofile":remote_user.profile}]

async def test_delete_friend_request(http_request,usernames,tokens,undelete_data):
    """
         user with username of usernames[0] sent a friend request to
         user with username of usernames[3]
    """
    json = {"username": usernames[3]}
    response = await http_request(path="/friendrequest", method=RequestMethod.DELETE, json=json,
                                  token=tokens[usernames[0]])
    assert response.status == 204
    await undelete_data(FriendRequests,sender=usernames[0],receiver=usernames[3])

async def test_invalid_delete_friend_request(http_request,usernames,tokens):
    """
        None of the users have sent a friend request to each other
    """
    json = {"username": usernames[2]}
    response = await http_request(path="/friendrequest", method=RequestMethod.DELETE, json=json,
                                  token=tokens[usernames[0]])
    assert response.status == 409