from app.friend.service import create_friend
from app.friend_request.service import create_friend_request, get_friend_request
from utils import RequestMethod


async def test_create_friend_request(
    http_request, current_user, current_user_token, remote_user
):
    remote_user, _ = await remote_user()
    response = await http_request(
        path="/friendrequest",
        method=RequestMethod.POST,
        json={"username": remote_user.username},
        token=current_user_token,
    )
    assert response.status_code == 201
    data = response.json()
    assert data == {
        "id": data["id"],
        "sender": current_user.username,
        "receiver": remote_user.username,
    }


async def test_invalid_create_friend_request(
    http_request, current_user, current_user_token, remote_user, db
):
    remote_user, _ = await remote_user()
    friend_request = await create_friend_request(
        db=db, current_user=remote_user, remote_user_username=current_user.username
    )
    await create_friend(
        db=db,
        current_user=current_user,
        remote_user_username=remote_user.username,
        current_friend_request=friend_request,
    )
    response = await http_request(
        path="/friendrequest",
        method=RequestMethod.POST,
        json={"username": remote_user.username},
        token=current_user_token,
    )
    assert response.status_code == 409


async def test_get_friend_requests(
    http_request, current_user, current_user_token, remote_user, db
):
    remote_user, _ = await remote_user()
    await create_friend_request(
        db=db, current_user=remote_user, remote_user_username=current_user.username
    )
    response = await http_request(
        path="/friendrequests", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            "receiver": current_user.username,
            "receiverprofile": current_user.profile,
            "sender": remote_user.username,
            "senderprofile": remote_user.profile,
        }
    ]


async def test_delete_friend_request(
    http_request, current_user, current_user_token, remote_user, db
):
    remote_user, _ = await remote_user()
    await create_friend_request(
        db=db, current_user=remote_user, remote_user_username=current_user.username
    )
    response = await http_request(
        path="/friendrequest",
        method=RequestMethod.DELETE,
        json={"username": remote_user.username},
        token=current_user_token,
    )
    assert response.status_code == 204
    friend_request = await get_friend_request(
        db=db, current_user=current_user, remote_user_username=remote_user.username
    )
    assert friend_request is None


async def test_invalid_delete_friend_request(
    http_request, current_user_token, remote_user
):
    remote_user, _ = await remote_user()
    response = await http_request(
        path="/friendrequest",
        method=RequestMethod.DELETE,
        json={"username": remote_user.username},
        token=current_user_token,
    )
    assert response.status_code == 409
