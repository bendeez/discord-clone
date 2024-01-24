import "./Requests.css"
import {useState,useContext} from "react"
import RequestsNav from "./RequestsNav.js"
import Online from "./Online.js"
import AllFriends from "./AllFriends.js"
import FriendRequests from "./FriendRequests.js"
import Blocked from "./Blocked.js"
import AddFriend from "./AddFriend.js"
import {Context} from "../../Context.js"

export default function Requests(){
    const {request} = useContext(Context)
    return(
        <div class="requests">
            <RequestsNav/>
            {request === "Online" ? (
                <Online/>
            ) : request === "All Friends" ? (
                <AllFriends/>
            ) : request === "Friend Requests" ? (
                <FriendRequests/>
            ) : request === "Blocked" ? (
                <Blocked/>
            ) : (
                <AddFriend/>
            )}
        </div>
    )
}