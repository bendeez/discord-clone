import "./RequestsNav.css"
import {useContext} from "react"
import {Context} from "../../Context.js"

export default function RequestsNav(){
    const {changeRequest,request} = useContext(Context)
    return(
        <div className="user-requests" id="user-requests">
            <div className="user-requests-nav" id="user-requests-nav">
                <p><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-user"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>Friends</p>
                <p onClick={() => changeRequest("Online")} className={request === "Online" ? "request-selected" : ""}>Online</p>
                <p onClick={() => changeRequest("All Friends")} className={request === "All Friends" ? "request-selected" : ""}>All</p>
                <p onClick={() => changeRequest("Friend Requests")} className={request === "Friend Requests" ? "request-selected" : ""}>Pending</p>
                <p onClick={() => changeRequest("Blocked")} className={request === "Blocked" ? "request-selected" : ""}>Blocked</p>
                <p onClick={() => changeRequest("Add Friend")} className={request === "Add Friend" ? "add-friend-selected" : "add-friend"}>Add Friend</p>
            </div>
        </div>
    )
}